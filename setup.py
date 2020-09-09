from setuptools import find_packages, setup

setup(
    name="irtools",
    version="1.9.0",
    description="Utilities for IR research",
    author="Binsheng Liu",
    author_email="liubinsheng@gmail.com",
    scripts=[
        "scripts/each_server.sh",
        "irtools/perplexity.py",
        "irtools/mypyrouge.py",
        "irtools/indri.py",
        "scripts/trec_eval.py",
        "scripts/wtl.py",
        "scripts/cleanit.py",
        "scripts/tokit.py",
        "scripts/spacit.py",
        "scripts/binarize.py",
        "scripts/sample.py",
        "scripts/eval_run.py",
        "scripts/trec2ans.py",
        "scripts/ans2trec.py",
        "scripts/label.py",
        "scripts/pair2list.py",
        "scripts/filter.py",
        "scripts/ttest_eval.py",
        "scripts/groupby.py",
        "scripts/lineplot_eval.py",
        "scripts/boxplot_eval.py",
        "scripts/euclidean_models.py",
        "scripts/lemmatize.py",
        "scripts/groupbys.py",
        "scripts/spacify.py",
        "scripts/subword_tf_idf.py",
        "scripts/binarize_columns.py",
        "scripts/trecweb2tsv.py",
        "scripts/cv_eval.py",
    ],
    packages=find_packages(exclude=["docs", "tests", "scripts"]),
    include_package_data=True,
    install_requires=[
        "unidecode",
        "tqdm",
        "scipy",
        "numpy",
        "more-itertools",
        "pandas",
        "ftfy",
        "lxml",
        "GPUtil",
    ],
)
