function requireElement(element, message) {
  if (!element) {
    throw new Error(message);
  }
  return element;
}

function createSectionTitle(text) {
  const title = document.createElement("h2");
  title.className = "palette-section-title";
  title.textContent = text;
  return title;
}

function createItemButton(item) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "palette-item";
  button.textContent = item.title;

  // Data attributes used by S007 drag-drop.
  if (typeof item.type === "string" && item.type) {
    button.dataset.nodeType = item.type;
  }

  return button;
}

export class PaletteManager {
  constructor({ root, categories }) {
    this.root = requireElement(root, "Palette root element is required");
    this.categories = categories ?? [];
  }

  render() {
    this.root.replaceChildren();

    for (const category of this.categories) {
      const section = document.createElement("section");
      section.className = "palette-section";

      section.appendChild(createSectionTitle(category.title));

      const list = document.createElement("div");
      list.className = "palette-items";

      for (const item of category.items ?? []) {
        list.appendChild(createItemButton(item));
      }

      section.appendChild(list);
      this.root.appendChild(section);
    }
  }
}
