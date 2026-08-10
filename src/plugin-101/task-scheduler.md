# Task scheduler

Sometimes you need to run something later, or on a repeating interval, without a player or command triggering it directly: a countdown, a periodic cleanup, batching up work over time. The scheduler lets you register a closure to run after a given number of ticks (20 ticks = 1 second).

## Scheduling a task

```rust
use pumpkin_plugin_api::scheduler::SchedulerExt;

fn on_load(&mut self, context: Context) -> Result<()> {
  context.schedule_delayed_task(20, |server| {
    server.log("One second has passed!");
  });
  Ok(())
}
```

- `schedule_delayed_task(delay_ticks, handler)` runs `handler` once, `delay_ticks` ticks from now.
- `schedule_repeating_task(delay_ticks, period_ticks, handler)` runs `handler` once after `delay_ticks`, then again every `period_ticks` after that.

Both return a `u32` task ID. Pass it to `cancel_task(task_id)` to stop the task before its next run.

`SchedulerExt` is implemented for `Server` as well as `Context`, so you can also schedule a task from inside an event handler or another task, anywhere you don't have a `Context` on hand.

## A note on blocking

A plugin only ever processes one call from the server at a time. While a scheduled task's closure is running, any event or command destined for that same plugin has to wait for it to return, they don't run concurrently. This is true of event handlers and commands too, but it's easiest to run into with the scheduler, since it's usually where people reach for heavier, longer-running work.

> [!WARNING]
> A slow task won't fail or get dropped, but it will hold up everything else queued for your plugin until it returns. If you have a genuinely large amount of work to get through, don't do it all in one call split it into batches and let a repeating task chip away at it instead:
>
> ```rust
> fn on_load(&mut self, context: Context) -> Result<()> {
>   context.schedule_repeating_task(20, 20, |server| {
>     // process one batch of work here, then return —
>     // the rest picks back up on the next run
>   });
>   Ok(())
> }
> ```
>
> Tune how often the batches run (more or less often than every 20 ticks) based on how much there is to get through and how urgent it is.
