ServerEvents.recipes(event => {
  const colors = [
    'white',
    'light_gray',
    'gray',
    'black',
    'brown',
    'red',
    'orange',
    'yellow',
    'lime',
    'green',
    'cyan',
    'light_blue',
    'blue',
    'purple',
    'magenta',
    'pink'
  ]

  colors.forEach(color => {
    event.recipes.create.compacting(
      `tfmg:${color}_concrete`,
      [
        Fluid.of(`createdieselgenerators:${color}_cement`, 1000)
      ]
    )
    .heated()
    .id(`crafttomuck:compacting/${color}_cement_to_tfmg_concrete`)
  })
})