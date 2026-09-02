export interface PointerPosition {
  x: number;
  y: number;
}

export function isClickGesture(
  start: PointerPosition,
  end: PointerPosition,
  threshold = 5,
): boolean {
  const deltaX =
    end.x - start.x;

  const deltaY =
    end.y - start.y;

  return (
    Math.hypot(
      deltaX,
      deltaY,
    ) <= threshold
  );
}
