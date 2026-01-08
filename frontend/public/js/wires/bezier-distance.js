/**
 * Calculate the distance from a point to a cubic bezier curve
 * Using parametric subdivision for reasonable approximation
 */

/**
 * Get point on cubic bezier curve at parameter t (0-1)
 */
function bezierPoint(t, p0, p1, p2, p3) {
    const t2 = t * t;
    const t3 = t2 * t;
    const mt = 1 - t;
    const mt2 = mt * mt;
    const mt3 = mt2 * mt;

    return {
        x: mt3 * p0.x + 3 * mt2 * t * p1.x + 3 * mt * t2 * p2.x + t3 * p3.x,
        y: mt3 * p0.y + 3 * mt2 * t * p1.y + 3 * mt * t2 * p2.y + t3 * p3.y,
    };
}

/**
 * Calculate distance between two points
 */
function distance(p1, p2) {
    const dx = p2.x - p1.x;
    const dy = p2.y - p1.y;
    return Math.sqrt(dx * dx + dy * dy);
}

/**
 * Find minimum distance from point to cubic bezier curve
 * Samples the curve at multiple points for approximation
 */
export function distanceToBezierCurve({ point, start, c1, c2, end, samples = 20 }) {
    let minDist = Infinity;

    for (let i = 0; i <= samples; i++) {
        const t = i / samples;
        const curvePoint = bezierPoint(t, start, c1, c2, end);
        const dist = distance(point, curvePoint);
        minDist = Math.min(minDist, dist);
    }

    return minDist;
}
