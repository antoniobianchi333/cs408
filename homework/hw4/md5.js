const crypto = require("crypto");

function computeMD5Hash(data) {
  const md5 = crypto.createHash("md5");
  md5.update(data);
  return md5.digest("hex");
}

function f(x) {
  let h = computeMD5Hash(x);
  if (h === "f0d7ce3a681c78829c8b8f090bc9f912") {
    console.log("Hash match!");
  } else {
    console.log("Hash mismatch");
  }
}

f("hello world");
