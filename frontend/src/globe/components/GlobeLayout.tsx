import type {
  ReactNode,
} from "react";

interface GlobeLayoutProps {
  header: ReactNode;
  sidebar: ReactNode;
  workspace: ReactNode;
  rightPanel: ReactNode;
  bottomPanel: ReactNode;
}

export function GlobeLayout({
  header,
  sidebar,
  workspace,
  rightPanel,
  bottomPanel,
}: GlobeLayoutProps) {
  return (
    <main className="radio-atlas">
      <header
        className="radio-atlas__header"
      >
        {header}
      </header>

      <aside
        className="radio-atlas__sidebar"
        aria-label="Globe controls"
      >
        {sidebar}
      </aside>

      <section
        className="radio-atlas__workspace"
        aria-label="Radio weather globe"
      >
        {workspace}
      </section>

      <aside
        className="radio-atlas__right-panel"
        aria-label="Information panel"
      >
        {rightPanel}
      </aside>

      <section
        className="radio-atlas__bottom-panel"
        aria-label="Activity panel"
      >
        {bottomPanel}
      </section>
    </main>
  );
}
