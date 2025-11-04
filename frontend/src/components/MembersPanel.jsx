import PropTypes from "prop-types";

function MembersPanel({
  form,
  setForm,
  members,
  isLoading,
  onSubmit,
  resetForm,
  onEdit,
  onDelete
}) {
  return (
    <div className="split-layout">
      <section className="card form-card">
        <h2 className="card-title">{form.id ? "Edit Member" : "Register Member"}</h2>
        <form className="stack" onSubmit={onSubmit}>
          <label>
            Full Name
            <input
              type="text"
              value={form.full_name}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, full_name: event.target.value }))
              }
              required
            />
          </label>
          <div className="actions">
            <button type="submit" className="primary" disabled={isLoading}>
              {form.id ? "Update Member" : "Add Member"}
            </button>
            {form.id && (
              <button type="button" className="secondary" onClick={resetForm}>
                Cancel
              </button>
            )}
          </div>
        </form>
      </section>

      <section className="card table-card">
        <div className="table-header">
          <h2 className="card-title">Member Directory</h2>
        </div>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Outstanding Debt</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {members.map((member) => (
                <tr key={member.id}>
                  <td>{member.full_name}</td>
                  <td>Rs.{Number(member.outstanding_debt).toFixed(2)}</td>
                  <td className="actions">
                    <button className="secondary" onClick={() => onEdit(member)}>
                      Edit
                    </button>
                    <button className="secondary" onClick={() => onDelete(member)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              {!members.length && (
                <tr>
                  <td colSpan="3">No members found</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

MembersPanel.propTypes = {
  form: PropTypes.shape({
    id: PropTypes.number,
    full_name: PropTypes.string.isRequired
  }).isRequired,
  setForm: PropTypes.func.isRequired,
  members: PropTypes.arrayOf(PropTypes.object).isRequired,
  isLoading: PropTypes.bool.isRequired,
  onSubmit: PropTypes.func.isRequired,
  resetForm: PropTypes.func.isRequired,
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired
};

export default MembersPanel;

