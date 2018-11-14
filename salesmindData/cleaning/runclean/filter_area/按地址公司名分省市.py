import pandas as pd


class fenshi(object):
    def getDate(self):
        # 不用改
        data_x = pd.read_excel("./对照表.xls", sheetname="区市对照表", usecols=[0, 1, 2])
        data_shi = pd.read_excel("./对照表.xls", sheetname="市市对照表", usecols=[0, 1, 2])

        #要查找的公司名和地址，第一列放公司名，第二列地址，第三列市，第四列省
        data_y = pd.read_excel("D:\python-program\数据\分市.xlsx", usecols=[0, 1, 2, 3])
        data_y=data_y.where(data_y.notnull(), "空值")
        print(data_y)
        return data_x,data_shi,data_y

    def deal(self,data_x,data_shi,data_y):
        # 遍历公司
        for inx in data_y.index:
            company_name = data_y.loc[inx].values[0]
            print("此次的公司名字是：%s" % (company_name))
            company_loc = data_y.loc[inx].values[1]
            zhuangt = "未找到"
            # 遍历市
            for indexs in data_shi.index:
                # 包含同一地区
                # 市名
                name_shi = data_shi.loc[indexs].values[0]
                name_deals = data_shi.loc[indexs].values[1]
                name_sheng= data_shi.loc[indexs].values[2]
                postionStrs = company_loc.find(name_shi)
                shi_end = postionStrs + len(name_shi)
                if postionStrs >= 0 and company_loc[shi_end] != "路" and company_loc[shi_end] != "区" and company_loc[
                    shi_end] != "县":
                    print("含有该市")
                    print(name_deals)
                    print(inx)
                    data_y.iloc[inx, 2] = name_deals
                    data_y.iloc[inx, 3] = name_sheng

                    print("修改后的数据为：==")
                    print(data_y.iloc[inx, 2])
                    zhuangt = "已找到"
                    break

            # 地区
            if zhuangt == "未找到":
                for indexs in data_x.index:
                    name_qu = data_x.loc[indexs].values[0]
                    name_deal = data_x.loc[indexs].values[1]
                    name_sheng = data_x.loc[indexs].values[2]
                    postionStr = company_loc.find(name_qu)
                    if postionStr >= 0:
                        print("含有该区")
                        print(name_deal)
                        print(inx)
                        data_y.iloc[inx, 2] = name_deal
                        data_y.iloc[inx, 3] = name_sheng
                        #  data_y[inx][2]=name_deal
                        print("修改后的数据为：==%s" % (name_deal))
                        print(data_y.iloc[inx, 2])
                        zhuangt = "已找到"
                        print("=====text======")
                        break
            print("市和区是否找到?????     %s" % (zhuangt))
            # 按公司名字查找
            if zhuangt == "未找到":
                if company_name.find("分公司") >= 0:
                    print("===含有分公司====")
                    # 遍历市
                    for indexss in data_shi.index:

                        name_shi_two = data_shi.loc[indexss].values[0]
                        name_deals = data_shi.loc[indexss].values[1]
                        name_shengs = data_shi.loc[indexss].values[2]
                        company_namefgs = company_name[company_name.find("分公司") - 4:company_name.find("分公司")]
                        if company_namefgs.find(name_shi_two) >= 0:
                            data_y.iloc[inx, 2] = name_deals + ";按分公司查找"
                            data_y.iloc[inx, 3] = name_shengs
                            #  data_y[inx][2]=name_deal
                            print("修改后的城市为：==%s" % (name_deals))
                            zhuangt = "已找到"
                            break
                else:
                    # 市
                    for indexssshi in data_shi.index:
                        # 包含同一地区
                        # 市名
                        name_shi_ = data_shi.loc[indexssshi].values[0]
                        name_dea = data_shi.loc[indexssshi].values[1]
                        name_shen = data_shi.loc[indexssshi].values[2]
                        if company_name.find(name_shi_) >= 0:
                            data_y.iloc[inx, 2] = name_dea + ";按公司查找"
                            data_y.iloc[inx, 3] = name_shen
                            #  data_y[inx][2]=name_deal
                            zhuangt = "已找到"
                            break





def main():
    dofs=fenshi()
    #deal(self,data_x,data_shi,data_y)
    (data_x,data_shi,data_y)=dofs.getDate()
    dofs.deal(data_x, data_shi, data_y)
    print(data_y)
    data_y.to_csv("D:\python-program\数据\地址OTMS1.csv",index=False )


if __name__ == '__main__':
    main()







