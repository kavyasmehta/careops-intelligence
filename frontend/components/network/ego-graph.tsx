"use client";

import type { ClientEgoNetwork, EgoNode } from "@/types/entities";

const NODE_COLORS: Record<string, string> = {
  Client: "var(--chart-1)",
  Employee: "var(--chart-2)",
  Payer: "var(--chart-3)",
  RiskFactor: "#ef4444",
  Appointment: "var(--chart-4)",
  Provider: "var(--chart-5)",
  Authorization: "#f59e0b",
  Service: "#94a3b8",
};

const SIZE = 600;
const CENTER = SIZE / 2;
const INNER_RADIUS = 170;
const OUTER_RADIUS = 260;

interface PositionedNode extends EgoNode {
  x: number;
  y: number;
}

/**
 * Hand-rolled radial layout (client at center, direct connections on an
 * inner ring, their own connections on an outer ring near the same
 * angle) rather than a general force-directed graph library — an ego
 * network is a star shape by construction, so a deterministic radial
 * layout reads more clearly than a physics simulation, with zero extra
 * dependencies.
 */
export function EgoGraph({ network }: { network: ClientEgoNetwork }) {
  const center = network.nodes.find((n) => n.type === "Client");
  if (!center) return null;

  const directEdges = network.edges.filter((e) => e.source === center.id);
  const directIds = new Set(directEdges.map((e) => e.target));
  const directNodes = network.nodes.filter((n) => directIds.has(n.id));

  const positioned = new Map<string, PositionedNode>();
  positioned.set(center.id, { ...center, x: CENTER, y: CENTER });

  const angleStep = (2 * Math.PI) / Math.max(directNodes.length, 1);
  directNodes.forEach((node, i) => {
    const angle = i * angleStep - Math.PI / 2;
    positioned.set(node.id, {
      ...node,
      x: CENTER + INNER_RADIUS * Math.cos(angle),
      y: CENTER + INNER_RADIUS * Math.sin(angle),
    });
  });

  // Second-degree nodes: placed near their parent's angle on an outer ring.
  directNodes.forEach((parent, i) => {
    const parentAngle = i * angleStep - Math.PI / 2;
    const childEdges = network.edges.filter((e) => e.source === parent.id);
    const spread = 0.35;
    childEdges.forEach((edge, j) => {
      if (positioned.has(edge.target)) return;
      const childNode = network.nodes.find((n) => n.id === edge.target);
      if (!childNode) return;
      const offset = childEdges.length > 1 ? (j / (childEdges.length - 1) - 0.5) * spread : 0;
      const angle = parentAngle + offset;
      positioned.set(childNode.id, {
        ...childNode,
        x: CENTER + OUTER_RADIUS * Math.cos(angle),
        y: CENTER + OUTER_RADIUS * Math.sin(angle),
      });
    });
  });

  const allEdges = network.edges.filter((e) => positioned.has(e.source) && positioned.has(e.target));
  const types = Array.from(new Set(network.nodes.map((n) => n.type)));

  return (
    <div className="space-y-2">
      <svg viewBox={`0 0 ${SIZE} ${SIZE}`} className="mx-auto w-full max-w-xl">
        {allEdges.map((edge, i) => {
          const s = positioned.get(edge.source)!;
          const t = positioned.get(edge.target)!;
          return (
            <line
              key={i}
              x1={s.x}
              y1={s.y}
              x2={t.x}
              y2={t.y}
              stroke="var(--border)"
              strokeWidth={1.5}
            />
          );
        })}
        {Array.from(positioned.values()).map((node) => {
          const isCenter = node.id === center.id;
          const radius = isCenter ? 22 : directIds.has(node.id) ? 14 : 8;
          return (
            <g key={node.id}>
              <circle cx={node.x} cy={node.y} r={radius} fill={NODE_COLORS[node.type] ?? "var(--muted-foreground)"}>
                <title>
                  {node.type}: {node.label}
                </title>
              </circle>
              {(isCenter || directIds.has(node.id)) && (
                <text
                  x={node.x}
                  y={node.y + radius + 14}
                  textAnchor="middle"
                  className="fill-foreground"
                  fontSize={isCenter ? 13 : 11}
                  fontWeight={isCenter ? 600 : 400}
                >
                  {node.label.length > 18 ? `${node.label.slice(0, 16)}…` : node.label}
                </text>
              )}
            </g>
          );
        })}
      </svg>
      <div className="flex flex-wrap justify-center gap-3 text-xs text-muted-foreground">
        {types.map((type) => (
          <span key={type} className="flex items-center gap-1.5">
            <span className="inline-block size-2.5 rounded-full" style={{ backgroundColor: NODE_COLORS[type] }} />
            {type}
          </span>
        ))}
      </div>
    </div>
  );
}
