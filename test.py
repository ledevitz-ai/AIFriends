from friends import friends_data, get_friend_by_id

print("Количество друзей:", len(friends_data))
print("Первый друг:", friends_data[0]["name"])

friend = get_friend_by_id(1)
print("Друг с ID 1:", friend["name"] if friend else "Не найден")