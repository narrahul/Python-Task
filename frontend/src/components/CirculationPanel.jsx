import PropTypes from "prop-types";
import { formatDate } from "../utils/format";

const STATUS_CLASS = {
  issued: "status-pill status-issued",
  returned: "status-pill status-returned"
};

function CirculationPanel({
  issueForm,
  setIssueForm,
  returnForm,
  setReturnForm,
  isLoading,
  booksInStock,
  issueCandidates,
  openTransactions,
  transactions,
  onIssue,
  onReturn
}) {
  return (
    <div className="split-layout circulation-layout">
      <section className="card form-card circulation-forms">
        <div className="stack">
          <div>
            <h2 className="card-title">Issue Book</h2>
            <form className="stack" onSubmit={onIssue}>
              <label>
                Select Book
                <select
                  value={issueForm.book_id}
                  onChange={(event) =>
                    setIssueForm((prev) => ({ ...prev, book_id: event.target.value }))
                  }
                  required
                >
                  <option value="">Select a book</option>
                  {booksInStock.map((book) => (
                    <option key={book.id} value={book.id}>
                      {book.title} ({book.available_copies} in stock)
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Select Member
                <select
                  value={issueForm.member_id}
                  onChange={(event) =>
                    setIssueForm((prev) => ({ ...prev, member_id: event.target.value }))
                  }
                  required
                >
                  <option value="">Select a member</option>
                  {issueCandidates.map((member) => {
                    const badges = [`Debt Rs.${member.outstanding.toFixed(2)}`];
                    if (member.isOverLimit) badges.push("over limit");
                    return (
                      <option
                        key={member.id}
                        value={member.id}
                        disabled={member.isOverLimit}
                      >
                        {member.full_name} ({badges.join(" | ")})
                      </option>
                    );
                  })}
                </select>
              </label>
              <button type="submit" className="primary" disabled={isLoading}>
                Issue Book
              </button>
            </form>
          </div>

          <div>
            <h2 className="card-title">Return Book</h2>
            <form className="stack" onSubmit={onReturn}>
              <label>
                Transaction
                <select
                  value={returnForm.transaction_id}
                  onChange={(event) =>
                    setReturnForm((prev) => ({
                      ...prev,
                      transaction_id: event.target.value
                    }))
                  }
                  required
                >
                  <option value="">Select an issued transaction</option>
                  {openTransactions.map((transaction) => (
                    <option key={transaction.id} value={transaction.id}>
                      #{transaction.id} - {(transaction.book_title || `Book ${transaction.book_id}`)} - {(transaction.member_name || `Member ${transaction.member_id}`)}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Rent Fee Collected
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={returnForm.payment_amount}
                  onChange={(event) =>
                    setReturnForm((prev) => ({
                      ...prev,
                      payment_amount: event.target.value
                    }))
                  }
                  required
                  placeholder="Enter amount (use 0 if unpaid)"
                />
              </label>
              <button type="submit" className="primary" disabled={isLoading}>
                Process Return
              </button>
            </form>
          </div>
        </div>
      </section>

      <section className="card table-card">
        <div className="table-header">
          <h2 className="card-title">Recent Activity</h2>
        </div>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Book</th>
                <th>Member</th>
                <th>Status</th>
                <th>Issue Date</th>
                <th>Return Date</th>
                <th>Fee</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((transaction) => (
                <tr key={transaction.id}>
                  <td>{transaction.id}</td>
                  <td>{transaction.book_title || transaction.book_id}</td>
                  <td>{transaction.member_name || transaction.member_id}</td>
                  <td>
                    <span className={STATUS_CLASS[transaction.status] || "status-pill"}>
                      {transaction.status}
                    </span>
                  </td>
                  <td>{formatDate(transaction.issue_date)}</td>
                  <td>{formatDate(transaction.return_date)}</td>
                  <td>
                    {transaction.rent_fee
                      ? `Rs.${Number(transaction.rent_fee).toFixed(2)}`
                      : "-"}
                  </td>
                </tr>
              ))}
              {!transactions.length && (
                <tr>
                  <td colSpan="7">No transactions yet</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

CirculationPanel.propTypes = {
  issueForm: PropTypes.shape({
    book_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    member_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired
  }).isRequired,
  setIssueForm: PropTypes.func.isRequired,
  returnForm: PropTypes.shape({
    transaction_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    payment_amount: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired
  }).isRequired,
  setReturnForm: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
  booksInStock: PropTypes.arrayOf(PropTypes.object).isRequired,
  issueCandidates: PropTypes.arrayOf(PropTypes.object).isRequired,
  openTransactions: PropTypes.arrayOf(PropTypes.object).isRequired,
  transactions: PropTypes.arrayOf(PropTypes.object).isRequired,
  onIssue: PropTypes.func.isRequired,
  onReturn: PropTypes.func.isRequired
};

export default CirculationPanel;







