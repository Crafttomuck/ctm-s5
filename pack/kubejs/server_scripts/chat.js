let LuckPerms;

const loadLuckPerms = () => {
  try {
    LuckPerms = Java.loadClass("net.luckperms.api.LuckPermsProvider").get();
  } catch (error) {
    LuckPerms = null;
  }
}

loadLuckPerms();

ServerEvents.loaded(event => {
  loadLuckPerms();
})

const WAYPOINT_PREFIX = "xaero-waypoint";

PlayerEvents.chat(event => {
  if (event.message.startsWith(WAYPOINT_PREFIX)) return;
  
  let { player, message } = event;
  let canFormatText = false;
  let prefix = "";
  
  if (LuckPerms) {
    const user = LuckPerms.getUserManager()['getUser(java.util.UUID)'](player.uuid)
    const userData = user.getCachedData();
    canFormatText = userData.getPermissionData().checkPermission('crafttomuck.chat.format_chat')
    prefix = userData.getMetaData().getPrefix() || "";
  }
  
  message = String(message);
  message = canFormatText == true ? global.format(message) : [{text: message, color: "white"}];
  const segments = global.format(`${prefix}${player.gameProfile.name}&r: `).concat(message);
  event.server.runCommandSilent(`tellraw @a ${JSON.stringify(segments)}`);
  event.cancel();
})