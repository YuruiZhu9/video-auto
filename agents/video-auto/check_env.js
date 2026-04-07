#!/usr/bin/env node
const { execSync } = require('child_process');
try {
  const r = require('canvas');
  console.log('canvas available');
} catch(e) {
  console.log('canvas not available:', e.message);
}
try {
  const r = require('sharp');
  console.log('sharp available');
} catch(e) {
  console.log('sharp not available:', e.message);
}
try {
  const r = require('jimp');
  console.log('jimp available');
} catch(e) {
  console.log('jimp not available:', e.message);
}
