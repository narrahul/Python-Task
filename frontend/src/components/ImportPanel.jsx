import PropTypes from "prop-types";

function ImportPanel({ form, setForm, isLoading, onSubmit }) {
  return (
    <section className="card form-card import-card">
      <h2 className="card-title">Import Books from Frappe Library</h2>
      <form className="stack" onSubmit={onSubmit}>
        <label>
          Number of books
          <input
            type="number"
            min="1"
            max="200"
            value={form.count}
            onChange={(event) =>
              setForm((prev) => ({ ...prev, count: event.target.value }))
            }
            required
          />
        </label>
        <div className="actions">
          <button type="submit" className="primary" disabled={isLoading}>
            Import Books
          </button>
        </div>
      </form>
    </section>
  );
}

ImportPanel.propTypes = {
  form: PropTypes.shape({
    count: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired
  }).isRequired,
  setForm: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
  onSubmit: PropTypes.func.isRequired
};

export default ImportPanel;

