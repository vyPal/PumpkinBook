# Task scheduler

Sometimes you need to run something later, or on a repeating interval, without a player or command triggering it directly: a countdown, a periodic cleanup, batching up work over time. The scheduler lets you register a closure to run after a given number of ticks (20 ticks = 1 second).

## Scheduling a task

```rust
use pumpkin_plugin_api::scheduler::SchedulerExt;

fn on_load(&self, context: Context) -> Result<()> {
  context.schedule_delayed_task(20, |server| {
    tracing::info!("One second has passed!");
  });
  Ok(())
}
```

- `schedule_delayed_task(delay_ticks, handler)` runs `handler` once, `delay_ticks` ticks from now.
- `schedule_repeating_task(delay_ticks, period_ticks, handler)` runs `handler` once after `delay_ticks`, then again every `period_ticks` after that.

Both return a `u32` task ID. Pass it to `cancel_task(task_id)` to stop the task before its next run.

`SchedulerExt` is implemented for `Server` as well as `Context`, so you can also schedule a task from inside an event handler or another task, anywhere you don't have a `Context` on hand.

## Closures and state

The handler has to be `Fn(Server) + Send + Sync + 'static`, not `FnMut`. The same task closure can be entered again while it is still running (see [Plugin state, handles and reentrancy](./plugin-logic.md#plugin-state-handles-and-reentrancy)), so a closure that wants to change something it captured needs interior mutability:

```rust
use std::sync::{atomic::{AtomicU32, Ordering}, Arc};
use pumpkin_plugin_api::scheduler::SchedulerExt;

fn on_load(&self, context: Context) -> Result<()> {
  let runs = Arc::new(AtomicU32::new(0));

  context.schedule_repeating_task(20, 20, move |_server| {
    let n = runs.fetch_add(1, Ordering::Relaxed) + 1;
    tracing::info!("Ran {n} times");
  });
  Ok(())
}
```

When your plugin unloads, its queued tasks are dropped and new ones are refused, so repeating tasks don't outlive it.

## A note on blocking

Only one call into a plugin runs at a time, and that holds **across plugins**: the server hands out a single turn at a time to all of them. While any plugin's task, event handler or command is running, every other plugin's callbacks wait in line behind it, yours included. In a test, a task that spun for four seconds in one plugin held back a task in a second plugin that was due a second later until the first one returned. The tasks are started outside the server tick, so a slow one doesn't freeze the tick loop by itself, but it does delay everything queued behind it, including the blocking [event handlers](./event-handlers.md#blocking-vs-non-blocking) the game is waiting on.

> [!WARNING]
> A slow task won't fail or get dropped, but it will hold up everything else queued for **every plugin** until it returns. If you have a genuinely large amount of work to get through, don't do it all in one call, split it into batches and let a repeating task chip away at it instead:
>
> ```rust
> fn on_load(&self, context: Context) -> Result<()> {
>   context.schedule_repeating_task(20, 20, |server| {
>     // process one batch of work here, then return,
>     // the rest picks back up on the next run
>   });
>   Ok(())
> }
> ```
>
> Tune how often the batches run (more or less often than every 20 ticks) based on how much there is to get through and how urgent it is.
