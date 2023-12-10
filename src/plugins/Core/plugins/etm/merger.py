from .item import Item


def merge_item_list(original_item_list: list[Item]) -> list[Item]:
    item_list: list[Item] = []
    for item in original_item_list:
        for item2 in item_list:
            if (
                item2.item_id == item.item_id
                and item2.data == item.data
                and item2.count < item2.data["maximum_stack"]
            ):
                count = min(item2.data["maximum_stack"] - item2.count, item.count)
                item.count -= count
                item2.count += count
            if item.count == 0:
                break
        else:
            if item.count <= item.data["maximum_stack"]:
                item_list.append(item)
            else:
                count = item.count
                item.count = 1
                item_list += merge_item_list([item for _ in range(count)])
    return item_list
