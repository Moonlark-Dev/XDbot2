import os


def get_version(is_develop):
    # 判断开始提交
    latest_tags = os.popen("git tag").read().splitlines()[-3:]
    if latest_tags[1].split(".")[1] == latest_tags[2].split(".")[1]:
        start_tag = latest_tags[2]
        v1 = int(latest_tags[2].split(".")[1]) + 1
    else:
        start_tag = latest_tags[1]
        v1 = int(latest_tags[2].split(".")[1])
    # print(latest_tags, start_tag)
    commit_count = int(
        os.popen(f'git rev-list --count {start_tag}..').read()) - 1
    all_commit_count = int(os.popen(f'git rev-list --count HEAD').read())
    return f"v2.{v1}.{commit_count}{'-dev' if is_develop else ''} ({all_commit_count})"
