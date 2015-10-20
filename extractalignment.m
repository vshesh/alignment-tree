(* ::Package:: *)

Alignments[data_]:= StringJoin[ToString@#1[[2]],"-",ToString@#1[[3]] ]&/@#1&/@(Sort[#1, #1[[2]]*1000+#1[[3]] < #2[[2]]*1000+#2[[3]] &] &/@Gather[Select[#1-{0,1,1}&/@data[[;;,;;3]], #1[[2]]>=0&&#1[[3]]>=0&],#1[[1]]==#2[[1]] &])//TableForm

