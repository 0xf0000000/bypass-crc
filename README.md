CRC Patcher

Descrição

Este script calcula e aplica bytes de correção em arquivos para modificar o valor CRC-32 para um valor específico, sem alterar o conteúdo original do arquivo.

Funcionalidade

· Calcula o CRC-32 atual do arquivo
· Determina os bytes necessários para alcançar o CRC-32 desejado
· Cria uma nova versão do arquivo com os bytes de correção adicionados no final

Como usar no Termux

1. Instale o Python (se necessário):

```bash
pkg install python
```

1. Salve o script como crc.py
2. Execute o script:

```bash
python crc.py arquivo.txt 0x12345678
```

Sintaxe

```bash
python crc.py <arquivo> <crc_alvo>
```

Parâmetros

· <arquivo>: Nome do arquivo a ser modificado
· <crc_alvo>: Valor CRC desejado (em hexadecimal com 0x ou decimal)

Exemplos

```bash
python crc.txt documento.pdf 0xdeadbeef
python crc.txt imagem.jpg 1234567890
```

Resultado

O script gera um novo arquivo com sufixo _patched contendo os bytes de correção adicionados. O CRC do novo arquivo corresponderá ao valor especificado.
