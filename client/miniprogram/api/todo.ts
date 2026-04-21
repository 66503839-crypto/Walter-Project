/** TODO API 封装。 */
import { request } from '../utils/request';

export interface Todo {
  id: number;
  title: string;
  content: string | null;
  done: boolean;
  priority: number;
  created_at: string;
  updated_at: string;
}

export const listTodos = () =>
  request<Todo[]>({ url: '/todos' });

export const createTodo = (title: string, content?: string, priority = 0) =>
  request<Todo>({ url: '/todos', method: 'POST', data: { title, content, priority } });

export const updateTodo = (id: number, patch: Partial<Pick<Todo, 'title' | 'content' | 'done' | 'priority'>>) =>
  request<Todo>({ url: `/todos/${id}`, method: 'PATCH', data: patch });

export const deleteTodo = (id: number) =>
  request<{ id: number }>({ url: `/todos/${id}`, method: 'DELETE' });
