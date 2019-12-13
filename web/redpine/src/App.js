import React, { useEffect } from "react";
import "./App.css";
import Cytoscape from "cytoscape";
// import popper from "cytoscape-popper";
import CytoscapeComponent from "react-cytoscapejs";
import COSEBilkent from "cytoscape-cose-bilkent";
import json from "./sample.json";

Cytoscape.use(COSEBilkent);

function App() {

  return (
    <CytoscapeComponent
      elements={json}
      style={{ width: "100%", height: "100%" }}
      layout={{ name: "cose-bilkent", fit: true }}
      stylesheet={[
        {
          selector: "node",
          style: {
            "background-color": "#E80018",
            label: "data(label)",
            "font-size": 1,
            width: 5,
            height: 5
          }
        },
        {
          selector: "edge",
          style: {
            width: 0.2,
            "curve-style": "bezier",
            "line-color": "#E80018",
            "target-arrow-color": "black",
            "target-arrow-shape": "triangle",
            "arrow-scale": 0.5
            // label: "data(label)"
          }
        }
      ]}
    />
  );
}

export default App;
