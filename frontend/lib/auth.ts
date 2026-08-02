// Auth Client Utilities and React Route Guard Hook

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export interface UserClaims {
  sub: string;
  role: 'admin' | 'employee' | 'manager';
  department_id: string;
  exp: number;
}

export function parseJwt(token: string): UserClaims | null {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch {
    return null;
  }
}

export function getUserClaims(): UserClaims | null {
  if (typeof window === 'undefined') return null;
  const token = localStorage.getItem('token');
  if (!token) return null;
  return parseJwt(token);
}

export function useRequireRole(allowedRoles: Array<'admin' | 'employee' | 'manager'>) {
  const router = useRouter();
  const [user, setUser] = useState<UserClaims | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const claims = getUserClaims();
    if (!claims) {
      router.push('/login');
    } else if (!allowedRoles.includes(claims.role)) {
      router.push('/login');
    } else {
      setUser(claims);
      setLoading(false);
    }
  }, [router]);

  return { user, loading };
}
