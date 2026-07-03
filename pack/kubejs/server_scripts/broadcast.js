ServerEvents.commandRegistry(event => {
  const { commands: Commands, arguments: Arguments } = event;
  
  event.register(
    Commands.literal('broadcast')
      .requires(source => source.hasPermission(2))
      .then(
        Commands.argument('message', Arguments.STRING.create(event))
          .executes(ctx => {
            const msg = Arguments.STRING.getResult(ctx, 'message');
            ctx.source.server.runCommandSilent(`tellraw @a ${JSON.stringify(global.format(msg))}`);
            return 1;
          })
      )   
  )

  event.register(
    Commands.literal('titlecast')
      .requires(source => source.hasPermission(2))
      .then(
        Commands.argument('title', Arguments.STRING.create(event))
          .executes(ctx => {
            const title = Arguments.STRING.getResult(ctx, 'title');
            ctx.source.server.runCommandSilent("/title @a title " + (JSON.stringify(global.format(title)) || "\"\""));
            return 1;
          })
          .then(
            Commands.argument('subtitle', Arguments.STRING.create(event))
              .executes(ctx => {
                const title = Arguments.STRING.getResult(ctx, 'title');
                const subtitle = Arguments.STRING.getResult(ctx, 'subtitle');
                ctx.source.server.runCommandSilent("/title @a subtitle " + JSON.stringify(global.format(subtitle)));
                ctx.source.server.runCommandSilent("/title @a title " + (JSON.stringify(global.format(title)) || "\"\""));
                return 1;
              })
          )
      )
  )
})