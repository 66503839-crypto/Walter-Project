import { createTodo, deleteTodo, listTodos, updateTodo, Todo } from '../../api/todo';

Page({
  data: {
    todos: [] as Todo[],
    inputTitle: '',
    loading: false,
  },

  async onShow() {
    await this.refresh();
  },

  async refresh() {
    this.setData({ loading: true });
    try {
      const list = await listTodos();
      this.setData({ todos: list });
    } finally {
      this.setData({ loading: false });
    }
  },

  onInput(e: WechatMiniprogram.Input) {
    this.setData({ inputTitle: e.detail.value });
  },

  async onAdd() {
    const title = this.data.inputTitle.trim();
    if (!title) return;
    await createTodo(title);
    this.setData({ inputTitle: '' });
    await this.refresh();
  },

  async onToggle(e: WechatMiniprogram.TouchEvent) {
    const id = Number(e.currentTarget.dataset.id);
    const done = e.currentTarget.dataset.done as boolean;
    await updateTodo(id, { done: !done });
    await this.refresh();
  },

  async onDelete(e: WechatMiniprogram.TouchEvent) {
    const id = Number(e.currentTarget.dataset.id);
    const confirmed = await wx.showModal({ title: '确认删除？', content: '' });
    if (!confirmed.confirm) return;
    await deleteTodo(id);
    await this.refresh();
  },
});
