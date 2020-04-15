#!/bin/bash
#
##SBATCH --nodes=1
#SBATCH --nodes=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --time=96:00:00
#SBATCH --mem=16GB
#SBATCH --job-name=marian_translation
#SBATCH --output=slurm_marian.out

# Make sure we have access to HPC-managed libraries.
module load anaconda3/5.3.1
module load python3/intel/3.7.0
module load cuda/9.2.88
module load boost/intel/1.62.0
module load cmake/intel/3.16.3

# Download pre-trained MT models
pip install mosestokenizer
pip install sentencepiece
pip install spacy-langdetect
mkdir models
cd models
mkdir $1-en
cd $1-en
if [ $1 == fr ]
then
   wget https://object.pouta.csc.fi/OPUS-MT-models/fr-en/opus-2020-02-26.zip
   unzip opus-2020-02-26.zip
else
   wget https://object.pouta.csc.fi/OPUS-MT-models/$1-en/opus-2019-12-18.zip
   unzip opus-2019-12-18.zip
fi
cd ..
cd ..

# Download WikiMatrix data
git clone https://github.com/facebookresearch/LASER/
cd LASER/tasks/WikiMatrix
rm extract.py
cd ..
cd ..
cd ..
mv extract.py LASER/tasks/WikiMatrix
if [ $1 == cs ] || [ $1 == de ]
then
   wget https://dl.fbaipublicfiles.com/laser/WikiMatrix/v1/WikiMatrix.$1-en.tsv.gz
   python3 LASER/tasks/WikiMatrix/extract.py \
  			--tsv WikiMatrix.$1-en.tsv.gz \
  			--bitext WikiMatrix.$1-en.txt \
  			--src-lang $1 --trg-lang en \
  			--threshold 0.75
else
   wget https://dl.fbaipublicfiles.com/laser/WikiMatrix/v1/WikiMatrix.en-$1.tsv.gz
   python3 LASER/tasks/WikiMatrix/extract.py \
  			--tsv WikiMatrix.en-$1.tsv.gz \
  			--bitext WikiMatrix.$1-en.txt \
  			--src-lang en --trg-lang $1 \
  			--threshold 0.75
fi

# Install Marian
git clone https://github.com/marian-nmt/marian
cd marian
mkdir build
cd build
cmake ..
make -j4
cd ..
cd ..

# Preprocess sentences
python3 preprocessor.py $1

# Implement translation
marian/build/marian-decoder --relative-paths true --models models/$1-en/opus.spm32k-spm32k.transformer-align.model1.npz.best-perplexity.npz --vocabs models/$1-en/opus.spm32k-spm32k.vocab.yml models/$1-en/opus.spm32k-spm32k.vocab.yml --beam-size 6 --normalize 1 --word-penalty 0 --mini-batch 1 --maxi-batch 1 --maxi-batch-sort src --output res_$1.txt < input_$1.txt

# Postprocess translation
python3 postprocessor.py $1


# Available languages: Indonesian(id), Japanese(ja), French(fr), Czech(cs), German(de)
