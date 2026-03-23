import "./Header.css";

export default function Header({ title, children }) {
  return (
    <div className="header">
      <h2>{title}</h2>
      <div>{children}</div>
    </div>
  );
}