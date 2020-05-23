def two_retry():
    success = False
    for _ in range(2):
        if not success:
            try:
                print(5/1)

                success = True
                print("yes")
            except Exception as e:
                print(e)


two_retry()
