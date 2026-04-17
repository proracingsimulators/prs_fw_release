# PRS Firmware Release Generator

Script em Python para organizar arquivos de release de firmware em uma estrutura versionada.

## Objetivo

Dado um diretório com arquivos `.json` de firmware e um arquivo `changes.txt`, o script gera uma estrutura de saída no formato:

```text
v1/{baseName}/{jsonName}/lastest.json
v1/{baseName}/{jsonName}/{version}.json
v1/{baseName}/{jsonName}/metadata.json
```

Isso permite manter histórico de versões por firmware e suportar evolução de formato (prefixo `v1`).

## Requisitos

- Python 3.8+
- Diretório de entrada contendo:
  - Um ou mais arquivos `.json` de firmware
  - Um arquivo `changes.txt` com as alterações da versão

## Uso

No diretório `prs_fw_release`, execute:

```bash
python generate_release.py <release_dir> <base_name>
```

### Parâmetros

- `release_dir`: diretório onde estão os arquivos `.json` e o `changes.txt`
- `base_name`: nome base do projeto

A versão é extraída automaticamente de cada arquivo JSON, usando a chave `Version` (ou `version`).

## Exemplo (Windows)

```powershell
python .\generate_release.py D:\projects\prs\prs_pedal_fw\release prs-pedal
```

## Estrutura gerada (exemplo)

Se existir um arquivo `sport.json` no diretório de entrada:

```text
v1/
  prs-pedal/
    sport/
      lastest.json
      1.2.3.json
      metadata.json
```

## Como o metadata.json é tratado

- Se não existir, é criado.
- Se já existir, é atualizado.
- O campo `latest` passa a apontar para a versão extraída do JSON.
- A seção `versions` recebe um novo item com:
  - `version`
  - `file`
  - `sourceFile`
  - `releasedAt`
  - `changesFile`
  - `changes`
- Se a versão já existir em `versions`, os dados dessa versão são substituídos.

## Validações feitas pelo script

- Falha se `release_dir` não existir.
- Falha se `changes.txt` não existir.
- Falha se não houver arquivos `.json` no diretório.
- Falha se algum `.json` estiver inválido.
- Falha se o JSON não tiver a chave `Version` ou `version`.

## Observações

- O script copia cada JSON de entrada para:
  - `lastest.json`
  - `{version}.json`
- O nome `lastest.json` está assim por compatibilidade com o comportamento atual do projeto.
