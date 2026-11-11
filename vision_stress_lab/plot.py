from __future__ import annotations

from html import escape
from pathlib import Path


def write_recall_svg(conditions: list[dict[str, object]], path: Path) -> None:
    width, height = 900, 460
    left, right, top, bottom = 80, 25, 40, 100
    plot_w, plot_h = width - left - right, height - top - bottom
    count = max(1, len(conditions))
    band = plot_w / count
    chunks = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
              '<rect width="100%" height="100%" fill="#fff"/>',
              '<text x="450" y="24" text-anchor="middle" font-family="sans-serif" font-size="18" font-weight="700">Target-presence recall by lighting condition</text>']
    for tick in range(6):
        value = tick / 5
        yy = top + (1 - value) * plot_h
        chunks.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{width-right}" y2="{yy:.1f}" stroke="#e5e7eb"/>')
        chunks.append(f'<text x="{left-10}" y="{yy+4:.1f}" text-anchor="end" font-family="sans-serif" font-size="11" fill="#4b5563">{value:.1f}</text>')
    for i, row in enumerate(conditions):
        value = row["recall"]
        cx = left + band * (i + 0.5)
        if value is None:
            chunks.append(f'<text x="{cx:.1f}" y="{top+plot_h/2:.1f}" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#6b7280">no positives</text>')
        else:
            bar_h = float(value) * plot_h
            chunks.append(f'<rect x="{cx-band*0.28:.1f}" y="{top+plot_h-bar_h:.1f}" width="{band*0.56:.1f}" height="{bar_h:.1f}" rx="5" fill="#2878b5"/>')
            chunks.append(f'<text x="{cx:.1f}" y="{top+plot_h-bar_h-8:.1f}" text-anchor="middle" font-family="sans-serif" font-size="12">{float(value):.2f}</text>')
        chunks.append(f'<text x="{cx:.1f}" y="{top+plot_h+22}" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#111827">{escape(str(row["condition"]))}</text>')
        chunks.append(f'<text x="{cx:.1f}" y="{top+plot_h+41}" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#6b7280">n={row["images"]}</text>')
    chunks.append(f'<text transform="translate(20 {height/2}) rotate(-90)" text-anchor="middle" font-family="sans-serif" font-size="13">Recall</text>')
    chunks.append('</svg>')
    path.write_text("\n".join(chunks), encoding="utf-8")

