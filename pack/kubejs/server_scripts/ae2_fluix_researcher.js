// Strip the AE2 Fluix Researcher villager's "sell" trades for meteorite-gated
// items. With AE2 meteorites moved to the End, this villager would otherwise
// let players buy presses / certus / sky stone / fluix for emeralds and skip
// meteorite progression entirely. We remove only those sell trades; the
// buy-back trades (charged certus, silicon, quartz glass, matter ball) and the
// slime ball trade are left intact.
//
// Requires MoreJS (villagerTrades is a MoreJS server event).
MoreJS.villagerTrades((event) => {
  [
    'ae2:certus_quartz_crystal',
    'ae2:meteorite_compass',
    'ae2:sky_stone_block',
    'ae2:fluix_crystal',
    'ae2:calculation_processor_press',
    'ae2:engineering_processor_press',
    'ae2:logic_processor_press',
    'ae2:silicon_press',
  ].forEach((item) => {
    event.removeTrades({ professions: 'ae2:fluix_researcher', output: item });
  });
});
