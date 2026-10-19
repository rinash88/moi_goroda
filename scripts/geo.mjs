// Проецирует контур России, соседние страны и города в координаты плоскости 1000 × 600.
// Запуск: node scripts/geo.mjs node_modules/world-atlas/countries-50m.json data/cities.json data/map-data.json
import fs from 'fs';
import * as topo from 'topojson-client';
import * as simp from 'topojson-simplify';
import * as d3 from 'd3-geo';

const [atlasPath, citiesPath, outPath] = process.argv.slice(2);
let t = JSON.parse(fs.readFileSync(atlasPath));
t = simp.presimplify(t);
t = simp.simplify(t, 0.0004);
const countries = topo.feature(t, t.objects.countries);
const ru = countries.features.find(f => f.properties.name === 'Russia');

const W = 1000, H = 600;
const proj = d3.geoConicEqualArea().rotate([-98, 0]).parallels([50, 68]).fitExtent([[10, 10], [W - 10, H - 10]], ru);
proj.clipExtent([[-150, -150], [W + 150, H + 150]]);
const r1 = v => Math.round(v * 10) / 10;
const path = d3.geoPath(proj); path.digits(1);

const near = countries.features.filter(f => {
  if (f === ru || f.properties.name === 'Antarctica') return false;
  const b = d3.geoBounds(f);
  return b[1][1] > 30 && (b[0][0] > 10 || b[1][0] > 10) && b[0][0] < 180;
});
const land = near.map(f => path(f)).filter(Boolean).join('');
const ruPath = path(ru);

const cities = JSON.parse(fs.readFileSync(citiesPath));
for (const g of cities) for (const c of g.c) { const p = proj([c[2], c[1]]); c.push(r1(p[0]), r1(p[1])); }

fs.writeFileSync(outPath, JSON.stringify({ W, H, land, ru: ruPath, g: cities }));
console.log('map-data:', fs.statSync(outPath).size, 'bytes →', outPath);
