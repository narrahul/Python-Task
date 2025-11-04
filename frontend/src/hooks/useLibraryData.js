import { useCallback, useState } from "react";
import { booksApi, membersApi, transactionsApi, importApi } from "../api";

function extractItems(response) {
  if (Array.isArray(response)) {
    return response;
  }
  if (response && Array.isArray(response.items)) {
    return response.items;
  }
  return [];
}

export function useLibraryData() {
  const [books, setBooks] = useState([]);
  const [members, setMembers] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const withLoader = useCallback(async (task) => {
    setIsLoading(true);
    try {
      return await task();
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadBooks = useCallback(async (params) => {
    const response = await booksApi.fetchBooks(params);
    const items = extractItems(response);
    setBooks(items);
    return items;
  }, []);

  const loadMembers = useCallback(async (params) => {
    const response = await membersApi.fetchMembers(params);
    const items = extractItems(response);
    setMembers(items);
    return items;
  }, []);

  const loadTransactions = useCallback(async (params) => {
    const response = await transactionsApi.fetchTransactions(params);
    const items = extractItems(response);
    setTransactions(items);
    return items;
  }, []);

  const refreshAll = useCallback(
    () =>
      withLoader(async () => {
        await Promise.all([
          loadBooks(),
          loadMembers(),
          loadTransactions()
        ]);
      }),
    [loadBooks, loadMembers, loadTransactions, withLoader]
  );

  const createBook = useCallback(
    (payload) =>
      withLoader(async () => {
        await booksApi.createBook(payload);
        await loadBooks();
      }),
    [loadBooks, withLoader]
  );

  const updateBook = useCallback(
    (id, payload) =>
      withLoader(async () => {
        await booksApi.updateBook(id, payload);
        await loadBooks();
      }),
    [loadBooks, withLoader]
  );

  const deleteBook = useCallback(
    (id) =>
      withLoader(async () => {
        await booksApi.deleteBook(id);
        await loadBooks();
      }),
    [loadBooks, withLoader]
  );

  const createMember = useCallback(
    (payload) =>
      withLoader(async () => {
        await membersApi.createMember(payload);
        await loadMembers();
      }),
    [loadMembers, withLoader]
  );

  const updateMember = useCallback(
    (id, payload) =>
      withLoader(async () => {
        await membersApi.updateMember(id, payload);
        await loadMembers();
      }),
    [loadMembers, withLoader]
  );

  const deleteMember = useCallback(
    (id) =>
      withLoader(async () => {
        await membersApi.deleteMember(id);
        await loadMembers();
      }),
    [loadMembers, withLoader]
  );

  const issueBook = useCallback(
    (payload) =>
      withLoader(async () => {
        const transaction = await transactionsApi.issueBook(payload);
        await Promise.all([
          loadBooks(),
          loadTransactions()
        ]);
        return transaction;
      }),
    [loadBooks, loadTransactions, withLoader]
  );

  const returnBook = useCallback(
    (payload) =>
      withLoader(async () => {
        const result = await transactionsApi.returnBook(payload);
        await Promise.all([
          loadBooks(),
          loadMembers(),
          loadTransactions()
        ]);
        return result;
      }),
    [loadBooks, loadMembers, loadTransactions, withLoader]
  );

  const importBooks = useCallback(
    (payload) =>
      withLoader(async () => {
        const result = await importApi.importBooks(payload);
        await loadBooks();
        return result;
      }),
    [loadBooks, withLoader]
  );

  return {
    books,
    members,
    transactions,
    isLoading,
    refreshAll,
    loadBooks,
    loadMembers,
    loadTransactions,
    createBook,
    updateBook,
    deleteBook,
    createMember,
    updateMember,
    deleteMember,
    issueBook,
    returnBook,
    importBooks
  };
}

