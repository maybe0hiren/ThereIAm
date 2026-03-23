import "./Button.css";

export default function Button({ children, onClick, className = "", style, disabled }) {
  return (
    <button
      onClick={onClick}
      className={className}
      style={style}
      disabled={disabled}
    >
      {children}
    </button>
  );
}