.. role:: diffinsert
.. role:: diffdelete
.. highlight:: none


.. container:: terminal

   | (env) $ benchmarkstt --reference-type argument --hypothesis-type argument --reference 'THE REFERENCE TRANSCRIPT' --hypothesis 'the hypothesis transcript' --lowercase --wer --worddiffs
   | wer
   | ===
   |
   | 0.333333
   |
   | worddiffs
   | =========
   |
   | Color key: Unchanged \ :diffdelete:`Reference` \ :diffinsert:`:Hypothesis`
   |
   | ·the\ :diffdelete:`·reference`\ :diffinsert:`·hypothesis`·transcript
   |
   | (env) $

