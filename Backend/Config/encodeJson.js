const fs = require("fs");
const path = require("path");

const dataDir = path.join(__dirname, "../Data");

function jsonToToon(obj) {
  if (Array.isArray(obj) && typeof obj[0] === "object") {
    const keys = Object.keys(obj[0]);
    const header = `[${obj.length}]{${keys.join(",")}}:`;
    const rows = obj
      .map(o => "  " + keys.map(k => o[k]).join(","))
      .join("\n");
    return `${header}\n${rows}`;
  }

  if (typeof obj === "object" && obj !== null) {
    let result = "";
    for (const key of Object.keys(obj)) {
      const value = jsonToToon(obj[key]);
      result += `${key}:\n  ${value.replace(/\n/g, "\n  ")}\n`;
    }
    return result.trim();
  }

  return String(obj);
}

function convertJsonToToon(jsonPath) {
  const toonPath = jsonPath.replace(/\.json$/i, ".toon");
  console.log(`Converting: ${jsonPath} → ${toonPath}`);

  try {
    const raw = fs.readFileSync(jsonPath, "utf8");
    const data = JSON.parse(raw);
    const toon = jsonToToon(data);
    fs.writeFileSync(toonPath, toon, "utf8");
    console.log(`Saved: ${toonPath}\n`);
    return true;
  } catch (err) {
    console.error(`Failed to convert ${jsonPath}:`, err.message);
    return false;
  }
}

function walkAndConvert(folder) {
  const entries = fs.readdirSync(folder, { withFileTypes: true });

  let count = 0;

  for (const entry of entries) {
    const fullPath = path.join(folder, entry.name);

    if (entry.isDirectory()) {
      count += walkAndConvert(fullPath); 
    } else if (entry.isFile() && entry.name.endsWith(".json")) {
      if (convertJsonToToon(fullPath)) count++;
    }
  }

  return count;
}

const converted = walkAndConvert(dataDir);
console.log(`Done. Converted JSON files: ${converted}`);
