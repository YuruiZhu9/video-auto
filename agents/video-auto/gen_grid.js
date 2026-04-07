const sharp = require('sharp');
const path = require('path');
const fs = require('fs');

const slidesDir = '/workspace/agents/video-auto/slides';
const outputDir = '/workspace/agents/video-auto/video';
const gridPath = '/workspace/agents/video-auto/slides/slides_grid.png';
const videoGridPath = '/workspace/agents/video-auto/video/slides_grid.png';

fs.mkdirSync(outputDir, { recursive: true });

const images = fs.readdirSync(slidesDir)
  .filter(f => f.endsWith('.png'))
  .sort();
console.log('Found', images.length, 'slides:', images);

const W = 1920, H = 1080;
const cols = 3;
const rows = Math.ceil(images.length / cols);

const cellW = W, cellH = H;

async function main() {
  const composites = [];

  for (let i = 0; i < images.length; i++) {
    const imgPath = path.join(slidesDir, images[i]);
    const row = Math.floor(i / cols);
    const col = i % cols;
    const left = col * cellW;
    const top = row * cellH;
    
    composites.push({
      input: imgPath,
      left: left,
      top: top
    });
    console.log(`  Slide ${i+1}: ${images[i]} at (${left}, ${top})`);
  }

  // Create the base dark canvas
  const canvasWidth = W * cols;
  const canvasHeight = H * rows;

  // First, create a dark background
  const bg = await sharp({
    create: {
      width: canvasWidth,
      height: canvasHeight,
      channels: 3,
      background: { r: 10, g: 10, b: 26 }
    }
  }).png().toBuffer();

  // Composite all images onto the dark background
  const result = await sharp(bg)
    .composite(composites)
    .png()
    .toBuffer();

  // Save to slides dir
  await sharp(result).toFile(gridPath);
  console.log('Grid saved to:', gridPath);

  // Also save to video dir
  await sharp(result).toFile(videoGridPath);
  console.log('Also saved to:', videoGridPath);

  // Report dimensions
  const meta = await sharp(result).metadata();
  console.log('Grid dimensions:', meta.width, 'x', meta.height);
}

main().catch(e => {
  console.error('Error:', e.message);
  process.exit(1);
});
