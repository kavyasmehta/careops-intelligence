"use client";

import { useEffect, useState } from "react";

import { listClients } from "@/lib/api/clients";
import { listUsers } from "@/lib/api/users";
import type { Client, User } from "@/types/entities";

/**
 * Small reference datasets (all clients, all employees) fetched once and
 * looked up by id — used to render human-readable names in tables that
 * only store a `client_id`/`assigned_employee_id` foreign key. Fine at
 * this dataset size (250 clients, 10 employees); would move server-side
 * (e.g. a join or a batched lookup endpoint) at real scale.
 */
const MAX_PAGE_SIZE = 100; // backend's ListParams caps page_size at 100

export function useClientsLookup() {
  const [byId, setById] = useState<Map<string, Client>>(new Map());
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadAll() {
      const first = await listClients({ page: 1, page_size: MAX_PAGE_SIZE });
      const all = [...first.data];
      const totalPages = Math.ceil(first.meta.total / MAX_PAGE_SIZE);
      for (let page = 2; page <= totalPages; page++) {
        const next = await listClients({ page, page_size: MAX_PAGE_SIZE });
        all.push(...next.data);
      }
      setById(new Map(all.map((c) => [c.id, c])));
    }
    loadAll().finally(() => setIsLoading(false));
  }, []);

  return { clientsById: byId, isLoading };
}

export function useUsersLookup() {
  const [byId, setById] = useState<Map<string, User>>(new Map());
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    listUsers()
      .then((res) => {
        setUsers(res.data);
        setById(new Map(res.data.map((u) => [u.id, u])));
      })
      .finally(() => setIsLoading(false));
  }, []);

  return { usersById: byId, users, isLoading };
}
