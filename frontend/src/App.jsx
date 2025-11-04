import React, { useEffect, useMemo, useState } from "react";

import Tabs from "./components/Tabs";
import BooksPanel from "./components/BooksPanel";
import MembersPanel from "./components/MembersPanel";
import CirculationPanel from "./components/CirculationPanel";
import ImportPanel from "./components/ImportPanel";
import { useLibraryData } from "./hooks/useLibraryData";

const TABS = [
  { id: "books", label: "Books" },
  { id: "members", label: "Members" },
  { id: "circulation", label: "Circulation" },
  { id: "imports", label: "Import" }
];

const defaultBookForm = {
  id: null,
  title: "",
  authors: "",
  isbn: "",
  publisher: "",
  total_copies: 1
};

const defaultMemberForm = {
  id: null,
  full_name: ""
};

const defaultIssueForm = {
  book_id: "",
  member_id: ""
};

const defaultReturnForm = {
  transaction_id: "",
  payment_amount: ""
};

const defaultImportForm = {
  count: 20
};

function App() {
  const {
    books,
    members,
    transactions,
    isLoading,
    refreshAll,
    loadBooks,
    createBook,
    updateBook,
    deleteBook,
    createMember,
    updateMember,
    deleteMember,
    issueBook,
    returnBook,
    importBooks
  } = useLibraryData();

  const [bookForm, setBookForm] = useState(defaultBookForm);
  const [memberForm, setMemberForm] = useState(defaultMemberForm);
  const [issueForm, setIssueForm] = useState(defaultIssueForm);
  const [returnForm, setReturnForm] = useState(defaultReturnForm);
  const [importForm, setImportForm] = useState(defaultImportForm);
  const [bookSearch, setBookSearch] = useState("");
  const [activeTab, setActiveTab] = useState("books");

  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  const booksInStock = useMemo(
    () => books.filter((book) => Number(book.available_copies || 0) > 0),
    [books]
  );

  const issueCandidates = useMemo(
    () =>
      members.map((member) => {
        const outstanding = Number(member.outstanding_debt || 0);
        return {
          ...member,
          outstanding,
          isOverLimit: outstanding > 500
        };
      }),
    [members]
  );

  const openTransactions = useMemo(
    () => transactions.filter((transaction) => transaction.status === "issued"),
    [transactions]
  );

  const resetBookForm = () => setBookForm(defaultBookForm);
  const resetMemberForm = () => setMemberForm(defaultMemberForm);

  const handleEditBook = (book) => {
    setBookForm({
      id: book.id,
      title: book.title,
      authors: book.authors,
      isbn: book.isbn || "",
      publisher: book.publisher || "",
      total_copies: book.total_copies
    });
  };

  const handleEditMember = (member) => {
    setMemberForm({
      id: member.id,
      full_name: member.full_name
    });
  };

  const handleBookSubmit = async (event) => {
    event.preventDefault();
    const payload = {
      title: bookForm.title.trim(),
      authors: bookForm.authors.trim(),
      isbn: bookForm.isbn || undefined,
      publisher: bookForm.publisher || undefined,
      total_copies: Number(bookForm.total_copies)
    };

    try {
      if (bookForm.id) {
        await updateBook(bookForm.id, payload);
      } else {
        await createBook(payload);
      }
      resetBookForm();
    } catch (error) {
      window.alert(error.response?.data?.error || "Failed to save book");
    }
  };

  const handleBookSearch = async (value) => {
    setBookSearch(value);
    try {
      await loadBooks(value ? { search: value } : undefined);
    } catch (error) {
      window.alert(error.response?.data?.error || "Failed to search books");
    }
  };

  const handleDeleteBook = async (book) => {
    if (!window.confirm(`Delete book "${book.title}"?`)) return;
    try {
      await deleteBook(book.id);
    } catch (error) {
      window.alert(error.response?.data?.error || "Failed to delete book");
    }
  };

  const handleMemberSubmit = async (event) => {
    event.preventDefault();
    const payload = {
      full_name: memberForm.full_name.trim()
    };

    try {
      if (memberForm.id) {
        await updateMember(memberForm.id, payload);
      } else {
        await createMember(payload);
      }
      resetMemberForm();
    } catch (error) {
      window.alert(error.response?.data?.error || "Failed to save member");
    }
  };

  const handleDeleteMember = async (member) => {
    if (!window.confirm(`Delete member "${member.full_name}"?`)) return;
    try {
      await deleteMember(member.id);
    } catch (error) {
      window.alert(error.response?.data?.error || "Failed to delete member");
    }
  };

  const handleIssueSubmit = async (event) => {
    event.preventDefault();
    try {
      await issueBook({
        book_id: Number(issueForm.book_id),
        member_id: Number(issueForm.member_id)
      });
      setIssueForm(defaultIssueForm);
    } catch (error) {
      window.alert(error.response?.data?.error || "Failed to issue book");
    }
  };

  const handleReturnSubmit = async (event) => {
    event.preventDefault();
    try {
      const result = await returnBook({
        transaction_id: Number(returnForm.transaction_id),
        payment_amount: Number(returnForm.payment_amount || 0)
      });
      window.alert(
        `Book returned. Rent fee: Rs.${Number(result.rent_fee || 0).toFixed(2)}`
      );
      setReturnForm(defaultReturnForm);
    } catch (error) {
      window.alert(error.response?.data?.error || "Failed to process return");
    }
  };

  const handleImportSubmit = async (event) => {
    event.preventDefault();
    const payload = { count: Number(importForm.count) };
    try {
      const { imported, duplicates } = await importBooks(payload);
      window.alert(`Imported ${imported} books (duplicates skipped: ${duplicates})`);
      setImportForm(defaultImportForm);
    } catch (error) {
      window.alert(error.response?.data?.error || "Failed to import books");
    }
  };

  return (
    <>
      <header className="navbar">
        <div className="container">
          <h1>City Library Management</h1>
        </div>
      </header>

      <main className="container">
        <Tabs tabs={TABS} activeTab={activeTab} onChange={setActiveTab} />

        {activeTab === "books" && (
          <BooksPanel
            form={bookForm}
            setForm={setBookForm}
            books={books}
            isLoading={isLoading}
            onSubmit={handleBookSubmit}
            onSearch={handleBookSearch}
            searchValue={bookSearch}
            resetForm={resetBookForm}
            onEdit={handleEditBook}
            onDelete={handleDeleteBook}
          />
        )}

        {activeTab === "members" && (
          <MembersPanel
            form={memberForm}
            setForm={setMemberForm}
            members={members}
            isLoading={isLoading}
            onSubmit={handleMemberSubmit}
            resetForm={resetMemberForm}
            onEdit={handleEditMember}
            onDelete={handleDeleteMember}
          />
        )}

        {activeTab === "circulation" && (
          <CirculationPanel
            issueForm={issueForm}
            setIssueForm={setIssueForm}
            returnForm={returnForm}
            setReturnForm={setReturnForm}
            isLoading={isLoading}
            booksInStock={booksInStock}
            issueCandidates={issueCandidates}
            openTransactions={openTransactions}
            transactions={transactions}
            onIssue={handleIssueSubmit}
            onReturn={handleReturnSubmit}
          />
        )}

        {activeTab === "imports" && (
          <ImportPanel
            form={importForm}
            setForm={setImportForm}
            isLoading={isLoading}
            onSubmit={handleImportSubmit}
          />
        )}
      </main>
    </>
  );
}

export default App;




















