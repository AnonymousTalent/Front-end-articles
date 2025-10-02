import React, { useRef, useEffect } from "react";
import * as d3 from "d3";

const RadarChart = ({ data }) => {
  const ref = useRef();

  useEffect(() => {
    if (!data || data.length === 0) return;

    const svg = d3.select(ref.current);
    svg.selectAll("*").remove();

    const width = 500;
    const height = 300;
    const radius = Math.min(width, height) / 2 - 40;

    const g = svg
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${width / 2},${height / 2})`);

    // Add a scanning line animation
    const scanner = g.append("line")
      .attr("x1", 0)
      .attr("y1", 0)
      .attr("x2", radius)
      .attr("y2", 0)
      .attr("stroke", "rgba(0, 255, 0, 0.5)")
      .attr("stroke-width", 2);

    scanner.transition()
      .ease(d3.easeLinear)
      .duration(2000)
      .attrTween("transform", () => d3.interpolateString("rotate(0)", "rotate(360)"));

    // Simple circular layout for AI modules
    const angleStep = (2 * Math.PI) / data.length;
    data.forEach((d, i) => {
      const nodeX = Math.cos(i * angleStep - Math.PI / 2) * radius;
      const nodeY = Math.sin(i * angleStep - Math.PI / 2) * radius;

      const node = g.append("g")
        .attr("transform", `translate(${nodeX}, ${nodeY})`)
        .style("cursor", "pointer")
        .on("click", () => alert(`模組: ${d.name}\n狀態: ${d.status}\n日誌: ${d.log}`));

      node.append("circle")
        .attr("r", 25)
        .attr("fill", d.status === "ok" ? "#10B981" : d.status === "warn" ? "#F59E0B" : "#EF4444")
        .attr("stroke", "white")
        .attr("stroke-width", 2);

      node.append("text")
        .attr("text-anchor", "middle")
        .attr("dy", ".35em")
        .attr("fill", "white")
        .text(d.name);
    });
  }, [data]);

  return <svg ref={ref}></svg>;
};

export default RadarChart;
