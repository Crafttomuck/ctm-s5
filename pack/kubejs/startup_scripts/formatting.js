const colorMap = {
  0: "black",
  1: "dark_blue",
  2: "dark_green",
  3: "dark_aqua",
  4: "dark_red",
  5: "dark_purple",
  6: "gold",
  7: "gray",
  8: "dark_gray",
  9: "blue",
  a: "green",
  b: "aqua",
  c: "red",
  d: "light_purple",
  e: "yellow",
  f: "white",
};

const effectMap = {
  k: "obfuscated",
  l: "bold",
  m: "strikethrough",
  n: "underlined",
  o: "italic"
};

function matchAll(str, regex) {
  // 1. Ensure the global flag 'g' is set. Rhino will throw an error 
  // with exec() if you loop without it.
  if (!regex.global) {
    throw new Error("Regex must have the 'g' flag for matchAll polyfill.");
  }

  var matches = [];
  var match;
  
  // 2. The core loop: exec() returns a match array or null when no more matches are found.
  // The regex's lastIndex property is automatically updated by exec().
  while ((match = regex.exec(str)) !== null) {
    // 3. Add the match array to the results.
    matches.push(match);
    
    // Optional: Prevent an infinite loop on zero-length matches
    // (e.g., matching /^/g or /(?=a)/g).
    // This is good practice, though less common.
    if (match[0].length === 0) {
      regex.lastIndex++;
    }
  }

  // 4. Reset lastIndex for future uses of the regex object
  regex.lastIndex = 0;

  return matches;
}

global.format = (text) => {
  // split text into segments beginning with one or more "&" groups
  // for example: "&6&lgold and bold or &rdefault, &:ff00ffcustom" -> ["&6&lgold and bold or ", "&rdefault, ", "&:ff00ffcustom"]
  let textSegments = matchAll((String(text) || ""), /(?:&#[0-9a-fA-F]{6}|&[0-9a-fklmnor])*.+?(?=(?:&#[0-9a-fA-F]{6}|&[0-9a-fklmnor])|$)/g);

  let tellrawFormatSegments = [];
  let previousSegment = {};
  for (let textSegment of textSegments) {
    textSegment = textSegment[0];
    let ampCodeMatches = matchAll(textSegment, /(?:&#[0-9a-fA-F]{6}|&[0-9a-fklmnor])/g);

    let color = "white";
    let effects = {};
    for (let ampCodeMatch of ampCodeMatches) {
      let ampCode = ampCodeMatch[0];
      if (ampCode.length == 8) {
        // RGB value
        color = ampCode.slice(1);
      } else {
        let code = ampCode[1];
        if (Object.keys(effectMap).includes(code)) {
          effects[effectMap[code]] = true;
        } else if (Object.keys(colorMap).includes(code)) {
          color = colorMap[code];
        } else {
          // The only remaining possibility is &r
          color = "white";
          effects = {
            obfuscated: false,
            bold: false,
            strikethrough: false,
            underlined: false,
            italic: false,
          };
        }
      }
    }

    let text = /(?:&#[0-9a-fA-F]{6}|&[0-9a-fklmnor])*(.*)/.exec(textSegment)[1];

    previousSegment = Object.assign(previousSegment, {text: text, color: color})
    previousSegment = Object.assign(previousSegment, effects)
    tellrawFormatSegments.push(Object.assign({}, previousSegment))
  }
  return tellrawFormatSegments
}   