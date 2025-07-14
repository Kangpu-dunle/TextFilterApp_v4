def bind_sortable_tables(treeview):
    columns = treeview["columns"]
    for col in columns:
        treeview.heading(col, text=col, command=lambda _col=col: sort_column(treeview, _col, False))

def sort_column(treeview, col, reverse):
    # 排除 tags 中含 "summary" 的行
    data = [(treeview.set(k, col), k) for k in treeview.get_children("") if "summary" not in treeview.item(k, "tags")]
    try:
        data.sort(key=lambda t: int(t[0]), reverse=reverse)
    except ValueError:
        data.sort(key=lambda t: t[0], reverse=reverse)
    for i, (val, k) in enumerate(data):
        treeview.move(k, "", i)
    treeview.heading(col, command=lambda: sort_column(treeview, col, not reverse))
