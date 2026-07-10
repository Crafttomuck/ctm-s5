ServerEvents.recipes(event => {
  const colors = [
    'blue',
    'black',
    'brown',
    'cyan',
    'gray',
    'green',
    'light_blue',
    'light_gray',
    'lime',
    'magenta',
    'orange',
    'pink',
    'purple',
    'red',
    'white',
    'yellow'
  ]

  colors.forEach(color => {
    event.remove({ id: `swlm:color_glass_to_${color}` })
  })
})