#!/usr/bin/env python3
"""生成「英力士宁波·求职尽调报告」Word 文档。

数据来源：INEOS 官网新闻稿、企查查/爱企查/启信宝索引快照、招聘站公开页、财经媒体报道。
所有事实均标注来源与日期，未验证项在文末单列。
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

EA_BODY = "宋体"
EA_HEAD = "黑体"
ASCII_F = "Times New Roman"


def style_run(run, size=10.5, bold=False, ea=EA_BODY, ascii_f=ASCII_F, color=None):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = ascii_f
    run._element.rPr.rFonts.set(qn("w:eastAsia"), ea)
    if color:
        run.font.color.rgb = color


def heading(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        style_run(run, size=15 if level == 1 else 12.5, bold=True, ea=EA_HEAD,
                  ascii_f="Arial", color=RGBColor(0x1F, 0x3A, 0x5F))
    return h


def para(doc, text, size=10.5, bold=False, space_after=6, align=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.25
    if align:
        p.alignment = align
    run = p.add_run(text)
    style_run(run, size=size, bold=bold)
    return p


def bullet(doc, text, size=10.5):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.2
    run = p.add_run(text)
    style_run(run, size=size)
    return p


def make_table(doc, header, rows, widths=None, header_size=9.5, body_size=9.5):
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, h in enumerate(header):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.space_before = Pt(2)
        style_run(p.add_run(h), size=header_size, bold=True, ea=EA_HEAD, ascii_f="Arial")
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.line_spacing = 1.1
            style_run(p.add_run(str(val)), size=body_size)
    if widths:
        for r in t.rows:
            for i, w in enumerate(widths):
                r.cells[i].width = Cm(w)
    return t


def build(out_path):
    doc = Document()

    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.left_margin = Cm(2.2)
    sec.right_margin = Cm(2.2)
    sec.top_margin = Cm(2.2)
    sec.bottom_margin = Cm(2.2)

    normal = doc.styles["Normal"]
    normal.font.name = ASCII_F
    normal.font.size = Pt(10.5)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), EA_BODY)

    # 封面标题
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    style_run(title.add_run("英力士宁波 · 求职尽调报告"), size=22, bold=True,
              ea=EA_HEAD, ascii_f="Arial", color=RGBColor(0x1F, 0x3A, 0x5F))
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    style_run(sub.add_run("中石化英力士苯领高新材料（宁波）有限公司 / 英力士苯领高分子材料（宁波）有限公司"),
              size=10.5, ea=EA_BODY)
    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    style_run(meta.add_run("采集日期：2026-10-11　｜　用途：应聘前公司尽调"),
              size=9.5, ea=EA_BODY, color=RGBColor(0x60, 0x60, 0x60))

    # 一、结论摘要
    heading(doc, "一、结论摘要")
    para(doc, "宁波 ABS 项目是英力士在华明确要「保留」的资产。2026 年 6 月，英力士宁可赔付 1.2 亿美元也要退出中石化天津乙烯合资项目，"
              "但在同一批公告中强调继续正常运营宁波 60 万吨 ABS 合资项目，其战略被总结为「退大宗乙烯、留高端材料」。"
              "从母公司的取舍看，这家公司的安全边际高于英力士其他在华合资项目。")
    para(doc, "需要同时看清三点：其一，它是 50:50 中外合资，治理结构上中外双方各占一半；其二，外资母公司正在收缩中国大宗化工业务；"
              "其三，ABS 行业正处在国内大扩能周期，产品盈利承压。综合判断：适合追求稳定、规范、外企管理体系的求职者，"
              "不适合赌高增长或高奖金。")

    # 二、主体确认
    heading(doc, "二、主体确认：宁波有两个「英力士」")
    para(doc, "招聘网站上这两个法人经常混着写，投递前务必确认是哪一家。")
    make_table(
        doc,
        ["对比项", "实体 A（新厂 / ABS）", "实体 B（老厂 / PS）"],
        [
            ["全称", "中石化英力士苯领高新材料（宁波）有限公司", "英力士苯领高分子材料（宁波）有限公司"],
            ["曾用名", "英力士苯领高新材料（宁波）有限公司\n（2019-08-08 至 2022-12-06）", "—"],
            ["统一社会信用代码", "91330200MA2GT7Y92W", "913302110538084768"],
            ["成立日期", "2019-08-08", "2012-09-25"],
            ["注册资本", "32000 万美元", "91153.36 万人民币（实缴同额）"],
            ["法定代表人", "STEPHEN MARK HARRINGTON", "BEITZ MARK"],
            ["参保人数", "209 人", "未获取到"],
            ["地址", "镇海区澥浦镇宁波石化经济技术开发区海祥路 569 号", "镇海区宁波石化经济技术开发区明海北路 2388 号"],
            ["主营", "ABS 树脂，60 万吨/年", "聚苯乙烯（PS）等苯乙烯类树脂"],
        ],
        widths=[3.0, 6.5, 6.5],
    )
    para(doc, "实体 A 另有广州分公司。实体 B 曾获评宁波市制造业纳税 50 强、2015 年省级科技型中小企业。", size=10)

    # 三、公司现在的全名
    heading(doc, "三、这家公司现在的全名")
    para(doc, "如果你应聘的是那个 60 万吨 ABS 新厂，它现在的全名是：", bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    style_run(p.add_run("中石化英力士苯领高新材料（宁波）有限公司"), size=14, bold=True,
              ea=EA_HEAD, ascii_f="Arial", color=RGBColor(0xC0, 0x30, 0x30))
    para(doc, "对应的英文名是 INEOS Styrolution Sinopec Advanced Materials (Ningbo) Ltd.。")
    para(doc, "名称演变是理解这家公司股权变化的关键：2019 年 8 月 8 日成立时，它叫「英力士苯领高新材料（宁波）有限公司」，"
              "是英力士苯领亚太（INEOS Styrolution APAC Pte. Ltd.）独资；2022 年 7 月中国石化与英力士互换 50% 股权"
              "（中石化把上海赛科石化 50% 转让给英力士，换来这家公司 50%），同年 12 月 6 日公司才更名为现在带「中石化」前缀的名字。")
    para(doc, "因此前程无忧上那句「是英力士苯领全资子公司」已经过期两年多——HR 的公司简介没有跟着改。", size=10)

    # 四、领导层
    heading(doc, "四、领导层构成：国资还是外资")
    para(doc, "结论：这是典型的 50:50 中外合资治理结构，领导层是中外混编，不是单一国资或单一外资。"
              "对外代表权（法定代表人）在外方，日常经营（总经理）在外方，而副董事长与财务负责人由中方担任——"
              "财务负责人由中方派驻是合资公司里最常见的资金监控安排。", bold=True)
    make_table(
        doc,
        ["姓名", "职务", "背景判断", "依据"],
        [
            ["STEPHEN MARK HARRINGTON", "法定代表人", "外方", "英力士苯领（INEOS Styrolution）全球 CEO，2020-07-01 上任，2026 年仍以该身份就宁波项目公开表态"],
            ["张孝明", "副董事长", "中方", "中国籍，1981 年生，硕士；同时任宁波、天津两家合资公司副董事长"],
            ["TAY JUI SENG", "董事、经理（总经理）", "外方", "新加坡籍，英力士亚太体系"],
            ["杜倩倩", "财务负责人、董事", "中方", "中方派驻财务监控角色"],
            ["黎勇", "董事", "中方", "—"],
            ["胡智浩", "董事", "中方", "—"],
            ["楼馗峰", "董事（职务待核）", "中方", "—"],
            ["黄锡祥", "董事", "中方", "—"],
            ["方梅珠（Meizhu Fang）", "宁波 ABS 项目 CEO", "英力士方委派", "INEOS 官方新闻稿署名 CEO，奠基仪式由其主持"],
        ],
        widths=[3.4, 3.2, 2.0, 7.4],
    )
    para(doc, "同一套人马也管理天津公司（中石化英力士苯领高新材料（天津）有限公司，2024-06 成立，注册资本约 16.8 亿人民币）："
              "法定代表人 Stephen Mark Harrington、副董事长张孝明、经理方梅珠、董事 Mark Beitz 与芮福生、监事孙国炜。"
              "两家公司共用管理层，说明英力士苯领在中国的高新材料业务是一体化管理的。", size=10)
    para(doc, "待核实：董事长姓名未在公开索引中检索到。按中国合资公司惯例，法定代表人常兼董事长，"
              "即董事长很可能就是 Harrington，但这属于推断，面试时可直接向 HR 确认。", size=10)

    # 五、项目沿革
    heading(doc, "五、项目沿革")
    for line in [
        "2019-01　英力士苯领与宁波市政府签署战略合作框架协议",
        "2019-08-08　实体 A 成立（外资独资）",
        "2020-01　宣布在宁波建世界级 ABS 基地，60 万吨/年",
        "2020-12-18　奠基，选址镇海宁波石化经济技术开发区",
        "2021-11-16　镇海分局环评审批：年产 60 万吨 ABS 项目（调整）",
        "2022-07　中石化与英力士互换 50% 股权，中石化入股实体 A",
        "2022-12-06　实体 A 更名（加「中石化」前缀）",
        "2023-02　与中石化按 50:50 成立合资公司运营 ABS 项目",
        "2023-11-21　举行开业仪式，宁波市常务副市长、镇海区委书记、英国驻华使馆代表出席",
    ]:
        bullet(doc, line, size=10)
    para(doc, "项目定位：英力士集团在中国投资的第一个实体项目，也是国家发改委重大外资专班推进项目。", size=10)

    # 六、工厂硬指标
    heading(doc, "六、工厂硬指标")
    make_table(
        doc,
        ["指标", "数值", "来源"],
        [
            ["年产能", "60 万吨 ABS，采用 Terluran® 技术", "INEOS 官网新闻稿"],
            ["占地", "26.7 公顷（约 400 亩）", "INEOS 官网 / 宁波市发改委"],
            ["人员", "员工及承包商超过 360 名（参保 209 人，差额为承包商）", "INEOS 官网 / 企查查"],
            ["客户行业", "汽车、电子、家电、医疗、玩具 / 运动 / 休闲", "INEOS 官网新闻稿"],
            ["选址理由", "靠近原料供应、供应链贴近客户", "INEOS 官网新闻稿"],
        ],
        widths=[3.0, 8.0, 5.0],
    )

    # 七、股权与母公司动态
    heading(doc, "七、股权与母公司动态（最重要的一节）")
    para(doc, "2026 年英力士在华大调整：", bold=True)
    for line in [
        "2025-11　英力士与中石化谈判退出天津石化合资",
        "2026-06　签署协议，退出中石化英力士（天津）石化有限公司全部投资",
        "2026-08-03　英力士官宣，赔付 1.2 亿美元离场，理由：中国市场环境疲软、产能过剩、难盈利",
        "同期：上海赛科（SECCO）合资 2026 年二季度仍亏 3810 万欧元（同比收窄）",
        "2026-05　新设天津高新材料合资（苯领）",
    ]:
        bullet(doc, line, size=10)
    para(doc, "关键表述：英力士明确表示继续在中国其他合资企业保持正常运营，包括位于宁波的年产 60 万吨 ABS 合资项目。"
              "多家分析机构将其战略概括为「退大宗乙烯、留高端材料」。", bold=True)
    para(doc, "对求职者的含义：", bold=True)
    bullet(doc, "正面：宁波 ABS 属于被保留的「优质资产」，短期被剥离概率低于天津项目。", size=10)
    bullet(doc, "负面：外资方对中国化工整体环境判断偏保守；50:50 股权结构下任何一方战略调整都可能改变公司走向。", size=10)
    bullet(doc, "需留意：英力士是否进一步减持、中石化是否增持。", size=10)

    # 八、薪酬带宽
    heading(doc, "八、薪酬带宽")
    make_table(
        doc,
        ["岗位 / 口径", "薪资", "来源 / 日期"],
        [
            ["Technical Service Engineer 技术服务工程师", "15-25k · 13 薪", "猎聘 2026-03"],
            ["Lab Technician", "8-12k · 13 薪", "猎聘 2026-09"],
            ["产品经理 Commercial Product Manager", "3-4 万 · 13 薪", "职友集 2026-07"],
            ["按学历统计（大专）", "约 9.0K", "职友集 2023-08"],
            ["倒班岗（历史数据）", "平均约 11300 元；基本工资 4000-4500 元 + 倒班 / 夜宵 / 技能补贴", "360 问答 2023-01"],
        ],
        widths=[5.5, 6.0, 4.5],
    )
    para(doc, "其他薪酬信息（来源为 AI 摘要页，置信度低，需自行核实）：最低工资 9750 元/月 + 年终奖；"
              "福利含五险一金、补充医疗保险、免费班车。13 薪是这家公司招聘页的普遍口径，可作为谈薪基准。", size=10)

    # 九、招聘与门槛
    heading(doc, "九、招聘与门槛")
    bullet(doc, "前程无忧、猎聘、职友集均有活跃招聘页，最近更新 2026-09 至 2026-10。", size=10)
    bullet(doc, "岗位覆盖：技术服务工程师、实验室技术员、产品经理等。", size=10)
    bullet(doc, "学历门槛：职友集口径「专科和本科都可以，学历要求不高」。", size=10)
    bullet(doc, "猎聘标注公司规模「2000-5000 人」——与参保 209 人严重不符，属集团口径，不可采信。", size=10)

    # 十、ABS 三装置布局
    heading(doc, "十、英力士与中石化的 ABS 三装置布局（「120 万吨」的真相）")
    para(doc, "先把一个常见误解拆掉：把「120 万吨/年 ABS」当成宁波某家新厂的规模。"
              "它不是单厂产能，而是三套装置的总目标产能。", bold=True)
    para(doc, "2022-07 英力士苯领与中国石化宣布成立 50:50 的 ABS 合资公司，规划三套装置、总目标产能 120 万吨/年：", size=10)
    make_table(
        doc,
        ["装置", "规模", "选址", "运营主体", "进度"],
        [
            ["第一套", "60 万吨/年", "宁波石化经济技术开发区（镇海区澥浦镇海祥路 569 号）",
             "中石化英力士苯领高新材料（宁波）有限公司", "2023-11-21 开业，已投产"],
            ["第二套", "30 万吨/年", "天津南港乙烯项目集群（天津经开区南港工业区）",
             "中石化英力士苯领高新材料（天津）有限公司（2024-06 成立，注册资本 16.8 亿元）",
             "2023-08-30 签股东协议，中国石化负责建设，计划 2025-04 投产"],
            ["第三套", "30 万吨/年", "位置尚未确定", "合资公司", "截至 2024 年未见选址披露"],
        ],
        widths=[1.8, 2.2, 4.5, 5.0, 2.5],
    )
    para(doc, "合计 60 + 30 + 30 = 120 万吨/年。宁波那家就是 60 万吨，不存在「宁波新建 120 万吨」这回事。", bold=True)
    para(doc, "天津有两家，别混：", bold=True)
    bullet(doc, "中石化英力士（天津）石化有限公司：2023-08-01 成立，注册资本 177.03 亿元，运营 120 万吨/年乙烯"
                "（天津南港）+ 配套 30 万吨/年 ABS，参保 1006 人 → 英力士 2026-08-03 宣布退出，赔付 1.2 亿美元、"
                "分 24 个月付清，中石化全资持有，公司主体存续、员工劳动关系不变。", size=10)
    bullet(doc, "中石化英力士苯领高新材料（天津）有限公司：2024-06 成立，注册资本 16.8 亿元，30 万吨/年 ABS → 苯领系，保留。", size=10)
    para(doc, "对求职者的含义：宁波厂是三套装置里规模最大、唯一已投产的一套，也是英力士明确保留的资产。"
              "第三套选址未定，说明若继续扩产，宁波园区内已有地块与公用工程条件，具备再次扩建的基础——面试时可以问这一条。", size=10)

    # 十一、风险扫描
    heading(doc, "十一、风险扫描")
    bullet(doc, "实体 B 法律风险（企查查 2020-11 快照）：合作风险 0、经营异常 0、严重违法 0、股权出质 0、"
                "环保处罚 0、税收违法 0、行政处罚 1 起。", size=10)
    bullet(doc, "实体 A 环境信用评级 A，持排污许可证，标注「环评审批通过项目」；启信分 695。", size=10)
    bullet(doc, "未检索到实体 A 的诉讼、欠薪、劳动仲裁记录。", size=10)
    para(doc, "行业风险（真实且重要）：国内 ABS 正在大扩能——浙石化 160 万吨等新产能陆续投放。"
              "英力士苯领与中石化规划的 ABS 三套装置合计目标产能 120 万吨/年（宁波 60 + 天津 30 + 第三套 30，"
              "详见第十节）。ABS 是典型的产能过剩品种，产品价格与利润承压。这既是母公司退出大宗化工的背景，"
              "也可能影响这家工厂的效益与奖金。", size=10, bold=False)

    # 十二、红旗清单
    heading(doc, "十二、红旗清单")
    for line in [
        "外资母公司正在收缩中国大宗化工业务（天津项目已赔付离场）",
        "50:50 合资结构，战略随双方博弈变化",
        "ABS 行业处于扩能周期，产品盈利承压",
        "招聘页公司简介未更新（仍写「全资子公司」），说明 HR 材料维护不细",
        "参保仅 209 人，属中型企业，内部转岗空间有限",
        "员工口碑样本稀少（贴吧仅 2022 年一帖 19 条回复），无法交叉验证",
    ]:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(3)
        style_run(p.add_run("☐ " + line), size=10)

    # 十三、面试必问
    heading(doc, "十三、面试必问")
    for i, q in enumerate([
        "公司现在的股权比例是 50:50 吗？2026 年英力士退出天津项目后，宁波这边的股权或投资计划有变化吗？",
        "董事长和总经理分别由哪一方委派？决策链条是怎样的？",
        "60 万吨 ABS 现在实际产能利用率多少？第三套 30 万吨 ABS 装置的选址是否已定、是否可能落在宁波？",
        "这个岗位是新增编制还是补员？去年部门离职率如何？",
        "13 薪是固定的还是与绩效挂钩？年终奖近年发放情况？",
        "五险一金缴纳基数按全额还是最低基数？",
        "竞业限制范围与补偿标准？试用期长度、试用期薪资比例？",
    ], 1):
        para(doc, f"{i}. {q}", size=10, space_after=4)

    # 十四、证据台账
    heading(doc, "十四、证据台账")
    make_table(
        doc,
        ["结论", "来源", "日期"],
        [
            ["实体 A 参保 209 人、USCC 91330200MA2GT7Y92W", "爱企查 + 企查查（双源一致）", "2025-08 / 2026-06"],
            ["实体 A 注册资本 32000 万美元、成立 2019-08-08", "启信宝索引", "—"],
            ["实体 B 注册资本 91153.36 万、成立 2012-09-25", "水滴信用 + 企查查", "—"],
            ["主要人员名单（法定代表人、副董事长、董事等）", "爱企查 / 天眼查 / 企查查索引", "2025-2026"],
            ["Steve Harrington 为英力士苯领全球 CEO", "搜狐 / 百家号 / 艾邦高分子", "2020-06 / 2026-05"],
            ["天津公司管理层构成（对照）", "爱企查", "2024-2026"],
            ["60 万吨 / 26.7 公顷 / 360+ 人员 / Terluran 技术", "INEOS 官网新闻稿原文", "—"],
            ["中石化与英力士互换 50% 股权", "网易财经 / 腾讯新闻", "2022-07 / 2023-02"],
            ["英力士赔付 1.2 亿美元退出天津、保留宁波 ABS", "新浪财经 / 雪球 / 网易 / 中国化工信息周刊", "2026-08"],
            ["ABS 三装置布局：宁波 60 万吨 + 天津南港 30 万吨 + 第三套 30 万吨（选址未定）",
             "美通社 / 新浪财经 / 经济观察网 / 天津经开区官网", "2022-07 至 2024-06"],
            ["天津乙烯合资退出对价分 24 个月付清、公司主体存续", "中国化工信息周刊 / 流程工业 / 头条搜索", "2026-08"],
            ["薪资带宽", "猎聘 / 职友集招聘页", "2026-03 至 2026-09"],
            ["实体 B 行政处罚 1 起", "企查查风险页", "2020-11"],
        ],
        widths=[7.5, 5.0, 3.5],
    )

    # 十五、ABS 生产工艺与技术要点
    heading(doc, "十五、ABS 生产工艺与技术要点（面试准备）")
    heading(doc, "15.1 两条工艺路线，先分清", level=2)
    para(doc, "ABS（丙烯腈-丁二烯-苯乙烯共聚物）工业上有两条主流路线：", size=10)
    make_table(
        doc,
        ["路线", "原理", "优点", "缺点"],
        [
            ["乳液接枝掺混法",
             "丁二烯乳液聚合制胶乳 → 接枝 SM/AN 成接枝粉 → 与本体或悬浮 SAN 熔融掺混造粒",
             "橡胶含量可高达 50%，抗冲与光泽平衡好，牌号灵活",
             "流程长、耗水、产生大量含乳化剂废水，需破乳凝聚洗涤干燥"],
            ["连续本体法",
             "PBD 橡胶溶于苯乙烯 → 与 AN 连续聚合 → 相反转形成橡胶粒子 → 两级真空脱挥 → 直接造粒",
             "流程短、无乳化剂、无工艺废水、能耗低、投资省",
             "橡胶含量上限约 20%，橡胶粒径分布控制难度大"],
        ],
        widths=[2.6, 5.0, 4.2, 4.2],
    )
    para(doc, "行业综述的共识：从投资与环保角度看，连续本体法是最佳路线，新建大规模装置普遍采用。", size=10)
    para(doc, "宁波项目的口径：英力士苯领官方通稿明确该基地采用 Terluran® ABS 技术（60 万吨/年，2023-11-21 开业）。"
              "Terluran® 是英力士苯领（源自 BASF 苯乙烯业务）的通用级 ABS 品牌，主力工艺为连续本体法；"
              "60 万吨世界级规模叠加国内环保要求，也指向本体法。但需注意：一份国内行业产能表将"
              "「英力士苯领 60（2023 年）」标注为乳液法，与上述判断冲突。建议面试时直接确认装置工艺路线。", size=10)

    heading(doc, "15.2 原料", level=2)
    make_table(
        doc,
        ["原料", "作用", "要点"],
        [
            ["苯乙烯 SM", "连续相单体，构成 SAN 基体", "大宗进厂，需阻聚剂与氮封"],
            ["丙烯腈 AN", "共聚单体，提供耐化学性、刚性、耐热", "剧毒、易燃，密闭采样 + 在线检测报警"],
            ["聚丁二烯橡胶 PBD", "橡胶相，提供韧性", "本体法需先溶于 SM"],
            ["引发剂", "自由基引发", "过氧化物类"],
            ["链转移剂", "调节分子量", "叔十二烷基硫醇 TDM"],
            ["抗氧剂 / 稳定剂", "防热氧老化与黄变", "酚类 + 亚磷酸酯"],
            ["润滑剂 / 脱模剂", "改善加工", "硬脂酸盐、EBS"],
        ],
        widths=[3.4, 5.0, 7.6],
    )

    heading(doc, "15.3 反应过程（本体法五步）", level=2)
    for line in [
        "溶胶：PBD 在苯乙烯中溶解（50-60℃），配成橡胶含量 5-15% 的胶液，要求无凝胶块。",
        "连续聚合（核心）：胶液 + AN + 引发剂 + 链转移剂送入第一反应器（CSTR，强搅拌 + 换热），90-130℃、"
        "转化率 20-40%，发生相反转——SAN 生成量增加使两相体积比翻转，橡胶由连续相变为分散相，"
        "形成 0.3-1.5 μm 橡胶粒子并被接枝 SAN 包覆稳定；随后串联后段反应器升温至 130-160℃，转化率提至 60-80%。"
        "接枝率、橡胶粒径、凝胶含量在此决定，是本体法的技术核心。",
        "脱挥：两级真空脱挥（闪蒸 + 脱挥挤出机），真空度 < 5 kPa、温度 200-240℃，残单降至 1000 ppm 以下并回收精制。",
        "造粒：熔体换网过滤（除凝胶与杂质）→ 水下切粒 → 干燥 → 均化。",
        "掺混包装：按牌号加助剂与色母，在线检测熔指 MFR、冲击强度、维卡软化点、色差。",
    ]:
        bullet(doc, line, size=10)

    heading(doc, "15.4 常见问题与解决方案", level=2)
    make_table(
        doc,
        ["问题", "现象", "原因", "对策"],
        [
            ["橡胶粒子形态失控", "冲击强度低、光泽差、鱼眼",
             "相反转点控制不当（剪切强度、两相粘度比、接枝率不匹配）",
             "调整搅拌转速与桨型、分段控温、控制接枝率与链转移剂、调整 PBD 门尼粘度"],
            ["凝胶含量偏高", "表面晶点 / 黑点、过滤网压升快",
             "丁二烯双键在高温高剪切下交联、局部热点",
             "降低后段温度、缩短高温停留、消除换热与搅拌死区、加抗氧剂、提高过滤精度"],
            ["反应器 / 脱挥器结垢挂壁", "传热下降、搅拌电流升高、被迫停车清洗",
             "高粘度熔体在器壁与搅拌轴形成滞留层并长期受热交联",
             "定期化学 + 机械清洗、优化桨叶与器壁间隙、控制停留时间分布、防粘涂层、保持满釜运行"],
            ["残单（SM / AN）超标", "气味重、VOC 不合规、AN 残留超标", "脱挥不彻底",
             "提高真空度与温度、增加脱挥级数、薄膜脱挥扩大表面积、注入汽提剂、校验真空系统"],
            ["黄变 / 色差", "产品发黄、批间色差",
             "热氧老化、助剂不足、停留时间过长、金属离子污染",
             "优化抗氧剂配方、降低加工温度、设备内壁抛光防锈、控制回收单体质量"],
            ["分子量分布失控", "MFR 波动", "链转移剂控制不稳、原料杂质",
             "链转移剂流量闭环、在线熔指分析、控制 SM 中醛类与过氧化物含量"],
            ["单体自聚堵塞（安全）", "储罐 / 管线 / 回收系统堵塞", "SM、AN 自聚",
             "补加阻聚剂 TBC、控温、氮封、限制停留时间、排查死角；AN 按剧毒品管理"],
        ],
        widths=[3.0, 3.6, 4.4, 5.0],
    )

    heading(doc, "15.5 面试可以直接抛的问题", level=2)
    for line in [
        "这套装置是连续本体法还是乳液接枝掺混法？",
        "相反转段的橡胶粒径控制，主要靠搅拌剪切还是靠接枝率调节？",
        "脱挥后残单控制指标是多少？AN 残留能到多少 ppm？",
        "反应器结垢的清洗周期一般多久？",
        "橡胶是外购 PBD 还是自产胶乳？",
    ]:
        bullet(doc, line, size=10)

    # 十六、待验证项
    heading(doc, "十六、待验证项")
    for line in [
        "实体 A 董事长姓名（公开索引未收录，推断为法定代表人兼任）",
        "实体 A 当前确切股权比例与实缴资本（需企查查 / 天眼查实时页面）",
        "2026 年是否新增投资或调整产能",
        "第三套 30 万吨 ABS 装置选址（截至 2024 年公开报道均称「尚未确定」）",
        "第二套天津 30 万吨 ABS 装置是否按 2025-04 计划投产，以及英力士退出乙烯合资后该装置是否仍由合资公司运营",
        "真实员工评价（脉脉、看准网需登录；建议面试时直接问在职员工）",
    ]:
        bullet(doc, line, size=10)

    note = doc.add_paragraph()
    note.paragraph_format.space_before = Pt(12)
    style_run(note.add_run("说明：本报告为非上市主体尽调，巨潮资讯（cninfo）无该公司记录（已实测确认）。"
                           "工商数据来自第三方登记平台的公开索引快照，建议入职前用企查查 App 复核一次实时页面。"),
              size=9, ea=EA_BODY, color=RGBColor(0x70, 0x70, 0x70))

    doc.save(out_path)
    print("saved:", out_path)


if __name__ == "__main__":
    import sys
    build(sys.argv[1] if len(sys.argv) > 1 else "report.docx")
