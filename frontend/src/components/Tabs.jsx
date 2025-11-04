import PropTypes from "prop-types";

function Tabs({ tabs, activeTab, onChange }) {
  return (
    <nav className="tabs">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          className={`tab-button${activeTab === tab.id ? " active" : ""}`}
          onClick={() => onChange(tab.id)}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
}

Tabs.propTypes = {
  tabs: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired
    })
  ).isRequired,
  activeTab: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired
};

export default Tabs;
