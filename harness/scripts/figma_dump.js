// figma_dump.js — reviewer 전용 읽기 스크립트 (use_figma로 실행)
// 노드를 수정하지 않는다. 아래 두 상수만 바꿔서 그대로 실행한다.
//   PAGE_NAME : 'P4-screens' (평소) 또는 'TEST' (Figma 연결 시험)
//   FRAME_NAME: 'S1-final' 등. TEST 페이지면 null (페이지의 모든 최상위 프레임)
// 반환값(JSON 문자열)을 work/S{n}/p5-figma-dump.json 에 그대로 저장한다.

const PAGE_NAME = 'P4-screens';
const FRAME_NAME = 'S1-final';

const toHex = (c) =>
  '#' + [c.r, c.g, c.b].map((v) => Math.round(v * 255).toString(16).padStart(2, '0')).join('');

const paints = (list) =>
  Array.isArray(list)
    ? list.filter((p) => p.visible !== false).map((p) =>
        p.type === 'SOLID' ? { type: 'SOLID', hex: toHex(p.color) } : { type: p.type })
    : [];

function info(n) {
  const d = { id: n.id, name: n.name, type: n.type };
  if ('fills' in n) d.fills = paints(n.fills);
  if ('strokes' in n) d.strokes = paints(n.strokes);
  if ('cornerRadius' in n) {
    if (n.cornerRadius === figma.mixed) {
      d.cornerRadii = [n.topLeftRadius, n.topRightRadius, n.bottomRightRadius, n.bottomLeftRadius];
    } else if (n.cornerRadius) {
      d.cornerRadius = n.cornerRadius;
    }
  }
  if ('layoutMode' in n && n.layoutMode !== 'NONE') {
    d.itemSpacing = n.itemSpacing;
    d.paddingLeft = n.paddingLeft;
    d.paddingRight = n.paddingRight;
    d.paddingTop = n.paddingTop;
    d.paddingBottom = n.paddingBottom;
  }
  if (n.type === 'TEXT') {
    d.characters = n.characters;
    const fams = new Set();
    for (const seg of n.getStyledTextSegments(['fontName'])) fams.add(seg.fontName.family);
    d.fontFamilies = [...fams];
  }
  return d;
}

function walk(n, out) {
  if (n.visible === false) return;
  out.push(info(n));
  if ('children' in n) for (const c of n.children) walk(c, out);
}

const page = figma.root.children.find((p) => p.name === PAGE_NAME);
if (!page) return JSON.stringify({ error: 'page not found: ' + PAGE_NAME });
await page.loadAsync();

const frames = page.children
  .filter((n) => n.type === 'FRAME' && (FRAME_NAME === null || n.name === FRAME_NAME))
  .map((f) => {
    const nodes = [];
    walk(f, nodes);
    return { id: f.id, name: f.name, page: PAGE_NAME, width: f.width, height: f.height, nodes };
  });

return JSON.stringify({ page: PAGE_NAME, frames });
