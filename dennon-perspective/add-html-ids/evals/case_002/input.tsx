"use client";

function ProductCard({ name }: { name: string }) {
  return <div className="card"><b>{name}</b></div>;
}

export default function TestPage() {
  return (
    <div className="page-wrapper">
      <h1 id="case002_h1" className="title">Hello World</h1>
      <p id="heroCopy" className="desc">Some description here</p>
      <button className="cta" onClick={() => alert('hi')}>Click</button>
      <section className="features" id="scrollSection">
        <ProductCard name="Item 1" />
        <ProductCard name="Item 2" />
        <div id="case002_div" className="footer" />
      </section>
    </div>
  );
}
