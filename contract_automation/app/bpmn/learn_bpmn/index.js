/* jshint esversion: 6 */
import Modeler from "bpmn-js/lib/Modeler";

import propertiesPanelModule from "bpmn-js-properties-panel";
import propertiesProviderModule from "bpmn-js-properties-panel/lib/provider/camunda";

import "bpmn-js/dist/assets/diagram-js.css";
import "bpmn-js/dist/assets/bpmn-font/css/bpmn-embedded.css";
import "bpmn-js-properties-panel/dist/assets/bpmn-js-properties-panel.css";

import "./styles.css";

import diagram from "./diagram.bpmn";

const container = document.getElementById("container");

const modeler = new Modeler({
  container,
  keyboard: {
    bindTo: document
  },
  additionalModules: [propertiesPanelModule, propertiesProviderModule],
  propertiesPanel: {
    parent: "#properties-panel-parent"
  }
});

modeler
  .importXML(diagram)
  .then(({ warnings }) => {
    if (warnings.length) {
      console.log(warnings);
    }

    const canvas = modeler.get("canvas");

    canvas.zoom("fit-viewport");
  })
  .catch(err => {
    console.log(err);
  });