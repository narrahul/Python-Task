import PropTypes from "prop-types";

function BooksPanel({
  form,
  setForm,
  books,
  isLoading,
  onSubmit,
  onSearch,
  searchValue,
  resetForm,
  onEdit,
  onDelete
}) {
  return (
    <div className="split-layout">
      <section className="card form-card">
        <h2 className="card-title">{form.id ? "Edit Book" : "Add New Book"}</h2>
        <form className="stack" onSubmit={onSubmit}>
          <div className="stack-row">
            <label>
              Book Title
              <input
                type="text"
                value={form.title}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, title: event.target.value }))
                }
                required
              />
            </label>
            <label>
              Authors
              <input
                type="text"
                value={form.authors}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, authors: event.target.value }))
                }
                required
              />
            </label>
          </div>
          <div className="stack-row">
            <label>
              ISBN
              <input
                type="text"
                value={form.isbn}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, isbn: event.target.value }))
                }
              />
            </label>
            <label>
              Publisher
              <input
                type="text"
                value={form.publisher}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, publisher: event.target.value }))
                }
              />
            </label>
          </div>
          <label>
            Total Copies
            <input
              type="number"
              min="1"
              value={form.total_copies}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, total_copies: event.target.value }))
              }
              required
            />
          </label>
          <div className="actions">
            <button type="submit" className="primary" disabled={isLoading}>
              {form.id ? "Update Book" : "Add Book"}
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
          <h2 className="card-title">Catalogue</h2>
          <input
            type="search"
            placeholder="Search by book, author, publisher"
            value={searchValue}
            onChange={(event) => onSearch(event.target.value)}
          />
        </div>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Title</th>
                <th>Author</th>
                <th>Stock</th>
                <th>ISBN</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {books.map((book) => (
                <tr key={book.id}>
                  <td>
                    <div>{book.title}</div>
                    {book.publisher && <div className="badge">{book.publisher}</div>}
                  </td>
                  <td>{book.authors}</td>
                  <td>
                    {book.available_copies} / {book.total_copies}
                  </td>
                  <td>{book.isbn || "-"}</td>
                  <td className="actions">
                    <button className="secondary" onClick={() => onEdit(book)}>
                      Edit
                    </button>
                    <button className="secondary" onClick={() => onDelete(book)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              {!books.length && (
                <tr>
                  <td colSpan="5">No books found</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

BooksPanel.propTypes = {
  form: PropTypes.shape({
    id: PropTypes.number,
    title: PropTypes.string.isRequired,
    authors: PropTypes.string.isRequired,
    isbn: PropTypes.string,
    publisher: PropTypes.string,
    total_copies: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired
  }).isRequired,
  setForm: PropTypes.func.isRequired,
  books: PropTypes.arrayOf(PropTypes.object).isRequired,
  isLoading: PropTypes.bool.isRequired,
  onSubmit: PropTypes.func.isRequired,
  onSearch: PropTypes.func.isRequired,
  searchValue: PropTypes.string.isRequired,
  resetForm: PropTypes.func.isRequired,
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired
};

export default BooksPanel;











