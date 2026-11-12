import { useEffect, useRef } from "react";
import { useLocaleStore } from "../i18n";
import "./TheaterView.css";

const W = 240;
const H = 120;
const HZ = 88;

/** Deterministic pixel-art skyline, ported from the redesign prototype. */
function drawSky(cv: HTMLCanvasElement) {
  const g = cv.getContext("2d");
  if (!g) return;
  let seed = 7;
  const r = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const px = (x: number, y: number, c: string, w = 1, hh = 1) => {
    g.fillStyle = c;
    g.fillRect(x, y, w, hh);
  };
  const sky = ["#06070f", "#090b1a", "#0d1024", "#141530", "#1e1838", "#2c1c3e", "#41203f", "#5c2a3d", "#7a3a3a", "#9a5236"];
  const bh = HZ / sky.length;
  for (let y = 0; y < HZ; y++) {
    const i = Math.min(sky.length - 1, Math.floor(y / bh));
    for (let x = 0; x < W; x++) {
      const f = (y % bh) / bh;
      const dither = f > 0.6 && (x + y) % 2 === 0 && i < sky.length - 1;
      px(x, y, dither ? sky[i + 1] : sky[i]);
    }
  }
  for (let i = 0; i < 70; i++) {
    const y = Math.floor(r() * 40);
    px(Math.floor(r() * W), y, r() > 0.8 ? "#ffffff" : "#8b93b8");
  }
  g.fillStyle = "#f3e3b0";
  g.beginPath();
  g.arc(30, 18, 6, 0, 7);
  g.fill();
  g.fillStyle = sky[1];
  g.beginPath();
  g.arc(33, 16, 5, 0, 7);
  g.fill();

  const tower = (x: number, w: number, ht: number, body: string, lit: string[], density: number) => {
    px(x, HZ - ht, body, w, ht);
    for (let yy = HZ - ht + 2; yy < HZ - 1; yy += 2)
      for (let xx = x + 1; xx < x + w - 1; xx += 2)
        if (r() < density) px(xx, yy, lit[Math.floor(r() * lit.length)]);
  };
  for (let x = 0; x < W; ) {
    const w = 4 + Math.floor(r() * 7);
    tower(x, w, 12 + Math.floor(r() * 26), "#141a2b", ["#3a4466", "#4a3f5a"], 0.25);
    x += w + Math.floor(r() * 2);
  }

  const fx = 52, fy = 58, fr = 17;
  g.imageSmoothingEnabled = false;
  for (let a = 0; a < 6.283; a += 0.06)
    px(Math.round(fx + fr * Math.cos(a)), Math.round(fy + fr * Math.sin(a)), "#9aa3d6");
  for (let k = 0; k < 12; k++) {
    const a = k * 0.5236;
    for (let t = 2; t < fr; t += 2)
      px(Math.round(fx + t * Math.cos(a)), Math.round(fy + t * Math.sin(a)), "#4f5880");
    px(Math.round(fx + fr * Math.cos(a)), Math.round(fy + fr * Math.sin(a)), "#f0a83c");
  }
  for (let y = fy; y < HZ; y++) {
    px(fx - Math.floor((y - fy) / 3), y, "#5a6390");
    px(fx + Math.floor((y - fy) / 3), y, "#5a6390");
  }

  let x = 76;
  while (x < 140) {
    const w = 5 + Math.floor(r() * 6);
    tower(x, w, 26 + Math.floor(r() * 34), "#1b2336", ["#f0c36a", "#7fd8e6", "#f0a83c", "#cfd6ff"], 0.35);
    px(x + Math.floor(w / 2), HZ - 62 - Math.floor(r() * 4), r() > 0.5 ? "#e0504a" : "#1b2336");
    x += w + 1;
  }
  for (let y = 0; y < 9; y++) {
    const w = Math.round(Math.sqrt(81 - (8 - y) * (8 - y)) * 1.4);
    for (let xx = -w; xx <= w; xx++) px(110 + xx, HZ - 9 + y, (xx + y) % 2 === 0 ? "#5b5f72" : "#3d4152");
  }
  [150, 162, 174].forEach((bx) => {
    for (let y = HZ - 44; y < HZ; y++) {
      const lean = Math.floor((HZ - y) / 14);
      px(bx - lean, y, "#26304a", 7);
      px(bx + 7 - lean, y, "#1a2236", 2);
      if (y % 2 === 0)
        for (let k = 1; k < 7; k += 2)
          if (r() < 0.55) px(bx - lean + k, y, r() > 0.3 ? "#ffd88a" : "#9fe0ff");
    }
  });
  px(144, HZ - 48, "#3b4766", 46, 3);
  px(148, HZ - 49, "#7fd8e6", 34, 1);
  px(186, HZ - 48, "#3b4766", 4, 2);
  for (let k = 145; k < 189; k += 3) px(k, HZ - 46, "#f0a83c");

  const tree = (tx: number, ht: number, c: string) => {
    px(tx, HZ - ht, "#2c2438", 2, ht);
    for (let y = 0; y < 6; y++) {
      const w = 1 + y;
      px(tx - w + 1, HZ - ht - y, y % 2 ? c : "#3a2c48", w * 2);
    }
    px(tx - 5, HZ - ht - 6, c, 12);
  };
  tree(200, 18, "#c25fd0");
  tree(212, 24, "#e07ad6");
  tree(224, 14, "#9b6be0");
  tree(234, 20, "#c25fd0");
  for (let x2 = 190; x2 < W; x2++) if (r() < 0.6) px(x2, HZ - 2 - Math.floor(r() * 3), "#1f3a2c");

  // Water reflection
  for (let y = HZ; y < H; y++) {
    const d = y - HZ;
    const sy = HZ - 1 - d * 1.6;
    for (let xx = 0; xx < W; xx++) {
      const off = Math.round(Math.sin(y * 1.7 + xx * 0.15) * (1 + d / 10));
      const data = g.getImageData(Math.max(0, Math.min(W - 1, xx + off)), Math.max(0, Math.floor(sy)), 1, 1).data;
      const k = 0.45 - d * 0.01;
      px(xx, y, `rgb(${Math.round(data[0] * k + 6)},${Math.round(data[1] * k + 10)},${Math.round(data[2] * k + 22)})`);
    }
    if (d % 3 === 0) for (let xx = 0; xx < W; xx += 7 + Math.floor(r() * 9)) px(xx, y, "#2a3350", 3);
  }
  px(0, HZ, "#3a2a30", W, 1);
}

export function TheaterView() {
  const t = useLocaleStore((s) => s.t);
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const cv = ref.current;
    if (!cv) return;
    try {
      drawSky(cv);
    } catch {
      /* canvas unavailable (e.g. test env): leave blank */
    }
  }, []);

  return (
    <section className="panel theater">
      <div className="panel-title">
        <span>{t("game.theater")}</span>
      </div>
      <canvas ref={ref} width={W} height={H} aria-hidden="true" />
    </section>
  );
}
