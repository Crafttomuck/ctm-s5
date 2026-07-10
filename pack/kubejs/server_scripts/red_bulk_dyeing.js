ServerEvents.recipes(event => {
  const redPlanks = 'manyideas_core:red_planks';
  const allItems = Utils.getRegistry('minecraft:item').getKeys();

  allItems.forEach(item => {
    let itemStr = item.toString();
    if (Ingredient.of('#minecraft:planks').test(itemStr) && itemStr !== redPlanks) {
      event.recipes.create.splashing(
        [Item.of(redPlanks)],
        [itemStr]
      );
    }
  });
});