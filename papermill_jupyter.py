import fire

#The function does type inference through Fire
def jupyter_dag(fp: str):
    print(fp)
    print(type(fp))
    return

if __name__ == "__main__":
    fire.Fire()