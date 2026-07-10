ServerEvents.recipes(event => {
  event.remove({ id: 'create:crushing/limestone' })

  event.recipes.create.crushing([
    'tfmg:limesand',
    'garnished:crushed_salt',
    CreateItem.of(Item.of('minecraft:iron_nugget', 2), 0.1),
    CreateItem.of(Item.of('create:zinc_nugget', 2), 0.1)
  ], 'create:limestone')
})